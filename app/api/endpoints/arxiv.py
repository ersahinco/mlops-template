from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.api.deps import get_session
from app.models import QueryRecord, QueryResult
from app.schemas.requests import ArxivSearchRequest
from app.schemas.responses import QueryRecordResponse, QueryResultResponse
import requests
import feedparser
from datetime import datetime
from typing import List, Optional
import json
import logging
import csv
from io import StringIO

# Setup structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

router = APIRouter()

@router.post("/search", response_model=QueryRecordResponse, status_code=status.HTTP_201_CREATED)
async def search_arxiv(request: ArxivSearchRequest, session: AsyncSession = Depends(get_session)) -> QueryRecordResponse:
    if not (request.author or request.title or request.journal):
        logger.error("Invalid request parameters")
        raise HTTPException(status_code=400, detail="At least one of the query parameters (author, title, journal) must be provided.")
    
    query = []
    if request.author:
        query.append(f"au:{request.author}")
    if request.title:
        query.append(f"ti:{request.title}")
    if request.journal:
        query.append(f"jr:{request.journal}")
    query_str = "+AND+".join(query)
    
    url = f"https://export.arxiv.org/api/query?search_query={query_str}&max_results={request.max_query_results or 8}&sortBy=relevance&sortOrder=descending"
    logger.info(f"Querying arXiv with URL: {url}")
    try:
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to query arXiv API with status code {response.status_code}, URL: {url}")
            raise HTTPException(status_code=response.status_code, detail="Error querying arxiv API.")
    except requests.exceptions.RequestException as e:
        logger.error(f"arXiv API not available: {str(e)}")
        raise HTTPException(status_code=503, detail="arXiv API not available.")
    
    feed = feedparser.parse(response.content)
    num_results = int(feed.feed.get("opensearch_totalresults", 0))
    if num_results == 0:
        logger.info("No results found for the query.")
        raise HTTPException(status_code=404, detail="No results found.")
    
    query_record = QueryRecord(
        query=query_str,
        timestamp=datetime.utcnow(),
        status=response.status_code,
        num_results=num_results
    )
    
    session.add(query_record)
    await session.commit()
    await session.refresh(query_record)
    
    for entry in feed.entries:
        authors = ", ".join(author.name for author in entry.authors)
        query_result = QueryResult(
            author=authors,
            title=entry.title,
            journal=entry.get('arxiv_journal_ref', None),
            query_record_id=query_record.id,
            timestamp=datetime.utcnow()
        )
        session.add(query_result)
    
    await session.commit()
    logger.info(f"Query record created with ID {query_record.id} and {len(feed.entries)} results.")
    
    result = await session.execute(select(QueryRecord).options(joinedload(QueryRecord.results)).filter_by(id=query_record.id))
    query_record_with_results = result.unique().scalar_one()
    
    return query_record_with_results

@router.get("/queries", responses={
    200: {
        "description": "Return queries as JSON or a file",
        "content": {
            "application/json": {},
            "text/csv": {}
        }
    }
})
async def get_queries(
    query_timestamp_start: datetime,
    query_timestamp_end: datetime = None,
    download: bool = False,
    session: AsyncSession = Depends(get_session)
) -> Response:
    logger.info("Received request for queries with download option set to %s", download)
    query = select(QueryRecord).where(QueryRecord.timestamp >= query_timestamp_start)
    if query_timestamp_end:
        query = query.where(QueryRecord.timestamp <= query_timestamp_end)

    result = await session.execute(query)
    queries = result.scalars().all()
    
    if not queries:
        logger.warning("No queries found within the specified time range.")
        raise HTTPException(status_code=404, detail="No queries found in the specified range.")

    if download:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'query', 'timestamp', 'status', 'num_results'])
        for record in queries:
            writer.writerow([record.id, record.query, record.timestamp.isoformat(), record.status, record.num_results])
        
        output.seek(0)
        logger.info("Generating CSV file for download.")
        return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=queries.csv"})
    else:
        response_data = [{"id": record.id, "query": record.query, "timestamp": record.timestamp.isoformat(), "status": record.status, "num_results": record.num_results} for record in queries]
        logger.info("Returning JSON response with query results.")
        return JSONResponse(content=response_data)

@router.get("/results", response_model=list[QueryResultResponse], status_code=status.HTTP_200_OK)
async def get_results(
    session: AsyncSession = Depends(get_session),
    page: int = Query(0, ge=0),  # Ensure page is non-negative
    items_per_page: int = Query(10, ge=1)  # Ensure items_per_page is at least 1
) -> list[QueryResult]:
    logger.info("Fetching results with pagination - page %s, items per page %s", page, items_per_page)
    result = await session.execute(
        select(QueryResult).order_by(QueryResult.timestamp).offset(page * items_per_page).limit(items_per_page)
    )
    results = result.scalars().all()
    if not results:
        logger.warning("No query results found for the current page: %s", page)
        raise HTTPException(status_code=404, detail="No query results found.")

    logger.info("Returning query results.")
    return results
