from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.api_router import api_router, auth_router
from app.core.config import get_settings

app = FastAPI(
    title="Minimal fastapi-postgres template for MLOps role at Zeiss",
    version="6.0.0",
    description="The `/arxiv` endpoints can be directly tested using the ```Try it out``` feature in Swagger UI. Simply provide the necessary parameters or request body depending on the endpoint and execute the requests. No authentication is required to access these endpoints.",
    openapi_url="/openapi.json",
    docs_url="/",
)

app.include_router(auth_router)
app.include_router(api_router)

# Sets all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        str(origin).rstrip("/")
        for origin in get_settings().security.backend_cors_origins
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Guards against HTTP Host Header attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=get_settings().security.allowed_hosts,
)
