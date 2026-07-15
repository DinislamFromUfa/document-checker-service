from fastapi import APIRouter

from app.api.v1.endpoints.checks import check_router

api_router = APIRouter()

api_router.include_router(check_router)