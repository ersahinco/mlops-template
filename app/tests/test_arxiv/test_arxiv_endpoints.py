import json
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
from unittest.mock import patch, MagicMock
import time

from app.main import app
from app.models import QueryRecord, QueryResult, User
from app.schemas.requests import ArxivSearchRequest, QueryTimestampRequest
from datetime import datetime, timedelta

# Setup the test environment
@pytest.fixture
def mock_response():
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.content = json.dumps(json_data).encode('utf-8')

        def json(self):
            return self.json_data
    
    return MockResponse

# Test successful arXiv search (simplified)
@pytest.mark.asyncio
async def test_arxiv_search_successful(client: AsyncClient, default_user_headers: dict, session: AsyncSession):
    request_data = {
        "author": "Einstein",
        "title": "",
        "journal": "",
        "max_query_results": 8  # Default value or provided
    }
    response = await client.post(
        "/arxiv/search",
        headers=default_user_headers,
        json=request_data
    )
    assert response.status_code == status.HTTP_201_CREATED

# Test no results found
@pytest.mark.asyncio
async def test_arxiv_search_no_results(client: AsyncClient, default_user_headers: dict, session: AsyncSession, mock_response):
    with patch('requests.get', return_value=mock_response({'feed': {'opensearch_totalresults': '0', 'entries': []}}, 200)):
        request_data = {
            "author": "Nobody",
            "title": "",
            "journal": "",
            "max_query_results": 8
        }
        response = await client.post(
            "/arxiv/search",
            headers=default_user_headers,
            json=request_data
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

# Test invalid query parameters (all empty)
@pytest.mark.asyncio
async def test_arxiv_search_invalid_query(client: AsyncClient, default_user_headers: dict, session: AsyncSession, mock_response):
    request_data = {
        "author": "",
        "title": "",
        "journal": "",
        "max_query_results": 8
    }
    response = await client.post(
        "/arxiv/search",
        headers=default_user_headers,
        json=request_data
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

# Test arXiv API unavailability
@pytest.mark.asyncio
async def test_arxiv_api_unavailable(client: AsyncClient, default_user_headers: dict, session: AsyncSession, mock_response):
    with patch('requests.get', return_value=mock_response({}, 503)):  # Simulate API failure
        request_data = {
            "author": "Einstein",
            "title": "Relativity",
            "journal": "",
            "max_query_results": 8
        }
        response = await client.post(
            "/arxiv/search",
            headers=default_user_headers,
            json=request_data
        )

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

@pytest.mark.asyncio
async def test_get_queries_json_response(client: AsyncClient, default_user_headers: dict, session: AsyncSession):
    # Setup: create some query records in the database
    query_record_1 = QueryRecord(query="au:Einstein", timestamp=datetime.utcnow(), status=200, num_results=10)
    query_record_2 = QueryRecord(query="ti:Relativity", timestamp=datetime.utcnow() - timedelta(days=1), status=200, num_results=5)
    session.add_all([query_record_1, query_record_2])
    await session.commit()

    # Test: get queries within a time range
    response = await client.get(
        "/arxiv/queries",
        headers=default_user_headers,
        params={
            "query_timestamp_start": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "query_timestamp_end": datetime.utcnow().isoformat(),
            "download": False
        }
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["query"] == "au:Einstein"
    assert data[1]["query"] == "ti:Relativity"

@pytest.mark.asyncio
async def test_get_queries_csv_download(client: AsyncClient, default_user_headers: dict, session: AsyncSession):
    # Setup: create some query records in the database
    query_record_1 = QueryRecord(query="au:Einstein", timestamp=datetime.utcnow(), status=200, num_results=10)
    query_record_2 = QueryRecord(query="ti:Relativity", timestamp=datetime.utcnow() - timedelta(days=1), status=200, num_results=5)
    session.add_all([query_record_1, query_record_2])
    await session.commit()

    # Test: get queries within a time range as CSV download
    response = await client.get(
        "/arxiv/queries",
        headers=default_user_headers,
        params={
            "query_timestamp_start": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "query_timestamp_end": datetime.utcnow().isoformat(),
            "download": True
        }
    )

    assert response.status_code == status.HTTP_200_OK
    assert "text/csv" in response.headers["content-type"]
    assert "attachment; filename=queries.csv" in response.headers["content-disposition"]
    content = response.text
    assert "id,query,timestamp,status,num_results" in content
    assert "au:Einstein" in content
    assert "ti:Relativity" in content

@pytest.mark.asyncio
async def test_get_queries_no_results(client: AsyncClient, default_user_headers: dict, session: AsyncSession):
    # Test: get queries within a time range that returns no results
    response = await client.get(
        "/arxiv/queries",
        headers=default_user_headers,
        params={
            "query_timestamp_start": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "query_timestamp_end": datetime.utcnow().isoformat(),
            "download": False
        }
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "No queries found in the specified range."

@pytest.mark.asyncio
async def test_get_queries_invalid_timestamp_format(client: AsyncClient, default_user_headers: dict, session: AsyncSession):
    # Test: get queries with invalid timestamp format
    response = await client.get(
        "/arxiv/queries",
        headers=default_user_headers,
        params={
            "query_timestamp_start": "invalid-timestamp",
            "query_timestamp_end": datetime.utcnow().isoformat(),
            "download": False
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_get_results_with_pagination(client: AsyncClient, default_user_headers: dict, session: AsyncSession):
    # Setup: create some query results in the database
    query_record = QueryRecord(query="au:Einstein", timestamp=datetime.utcnow(), status=200, num_results=2)
    session.add(query_record)
    await session.commit()
    query_result_1 = QueryResult(author="Einstein", title="Relativity", journal="Journal A", query_record_id=query_record.id, timestamp=datetime.utcnow())
    query_result_2 = QueryResult(author="Newton", title="Physics", journal="Journal B", query_record_id=query_record.id, timestamp=datetime.utcnow() - timedelta(days=1))
    session.add_all([query_result_1, query_result_2])
    await session.commit()

    # Test: fetch results with pagination
    response = await client.get(
        "/arxiv/results",
        headers=default_user_headers,
        params={"page": 0, "items_per_page": 1}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["author"] == "Newton"

    response = await client.get(
        "/arxiv/results",
        headers=default_user_headers,
        params={"page": 1, "items_per_page": 1}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["author"] == "Einstein"

@pytest.mark.asyncio
async def test_get_results_no_results(client: AsyncClient, default_user_headers: dict, session: AsyncSession):
    # Test: fetch results when no results are found
    response = await client.get(
        "/arxiv/results",
        headers=default_user_headers,
        params={"page": 0, "items_per_page": 10}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "No query results found."

@pytest.mark.asyncio
async def test_get_results_order(client: AsyncClient, default_user_headers: dict, session: AsyncSession):
    # Setup: create some query results in the database
    query_record = QueryRecord(query="au:Einstein", timestamp=datetime.utcnow(), status=200, num_results=2)
    session.add(query_record)
    await session.commit()
    query_result_1 = QueryResult(author="Einstein", title="Relativity", journal="Journal A", query_record_id=query_record.id, timestamp=datetime.utcnow() - timedelta(days=1))
    query_result_2 = QueryResult(author="Newton", title="Physics", journal="Journal B", query_record_id=query_record.id, timestamp=datetime.utcnow())
    session.add_all([query_result_1, query_result_2])
    await session.commit()

    # Test: fetch results to check order
    response = await client.get(
        "/arxiv/results",
        headers=default_user_headers,
        params={"page": 0, "items_per_page": 2}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["author"] == "Einstein"
    assert data[1]["author"] == "Newton"

@pytest.mark.asyncio
async def test_get_results_invalid_pagination_params(client: AsyncClient, default_user_headers: dict, session: AsyncSession):
    # Test: fetch results with invalid pagination parameters
    response = await client.get(
        "/arxiv/results",
        headers=default_user_headers,
        params={"page": -1, "items_per_page": 10}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = await client.get(
        "/arxiv/results",
        headers=default_user_headers,
        params={"page": 0, "items_per_page": -10}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = await client.get(
        "/arxiv/results",
        headers=default_user_headers,
        params={"page": "invalid", "items_per_page": "invalid"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY