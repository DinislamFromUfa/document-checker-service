from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Document Checker Service started")

    yield

    print("Document Checker Service stopped")


app = FastAPI(
    title="Document Checker Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "service": "Document Checker Service",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}