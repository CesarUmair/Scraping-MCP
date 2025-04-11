from fastapi import APIRouter
from app.api import mcp
from app.api import ingestion

api_router = APIRouter()

# Include MCP router
api_router.include_router(mcp.router)

# Include ingestion router
api_router.include_router(ingestion.router)

# Include content router (for content management endpoints)
# Uncomment when content.py is fully implemented
# from app.api import content
# api_router.include_router(content.router) 