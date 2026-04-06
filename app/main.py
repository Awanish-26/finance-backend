from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.router import api_router
from app.core.config import settings
from app.db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Invalid request payload",
            "details": exc.errors(),
        },
    )


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(_: Request, __: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "error": "DUPLICATE_RESOURCE",
            "message": "Resource already exists",
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(api_router)
