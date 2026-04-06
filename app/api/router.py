from fastapi import APIRouter

from app.api.routes import auth, records, summaries, users

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(records.router, prefix="/records", tags=["records"])
api_router.include_router(
    summaries.router, prefix="/summaries", tags=["summaries"])
