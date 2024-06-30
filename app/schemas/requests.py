from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class BaseRequest(BaseModel):
    pass

class RefreshTokenRequest(BaseRequest):
    refresh_token: str

class UserUpdatePasswordRequest(BaseRequest):
    password: str

class UserCreateRequest(BaseRequest):
    email: EmailStr
    password: str

class ArxivSearchRequest(BaseModel):
    author: Optional[str] = Field(None, description="Author name to search for", example="John Doe")
    title: Optional[str] = Field(None, description="Title of the paper to search for", example="Quantum Computing")
    journal: Optional[str] = Field(None, description="Journal name to search for", example="Nature")
    max_query_results: int = Field(8, description="Maximum number of query results to return", example=8)

class QueryTimestampRequest(BaseModel):
    query_timestamp_start: datetime = Field(..., description="Start timestamp for query", example="2023-01-01T00:00:00")
    query_timestamp_end: Optional[datetime] = Field(None, description="End timestamp for query", example="2023-01-31T23:59:59")