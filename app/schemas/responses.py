from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional

class BaseResponse(BaseModel):
    class Config:
        orm_mode = True
        from_attributes = True

class AccessTokenResponse(BaseResponse):
    token_type: str = "Bearer"
    access_token: str
    expires_at: int
    refresh_token: str
    refresh_token_expires_at: int

class UserResponse(BaseResponse):
    user_id: str
    email: EmailStr

class QueryResultResponse(BaseModel):
    id: int
    author: str = Field(..., description="Authors of the result", example="John Doe, Jane Smith")
    title: str = Field(..., description="Title of the result", example="Quantum Computing")
    journal: Optional[str] = Field(None, description="Journal of the result", example="Nature")

    class Config:
        orm_mode = True

class QueryRecordResponse(BaseModel):
    id: int
    query: str = Field(..., description="Query string used", example="au:John Doe")
    timestamp: datetime = Field(..., description="Timestamp of the query", example="2023-01-01T00:00:00")
    status: int = Field(..., description="HTTP status code of the response", example=200)
    num_results: int = Field(..., description="Number of results found", example=42)
    results: List[QueryResultResponse] = Field(..., description="List of query results")

    class Config:
        orm_mode = True
