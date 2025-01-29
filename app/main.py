from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import videos
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    videos.router,
    prefix=f"{settings.API_V1_STR}/videos",
    tags=["videos"]
)

@app.get("/")
async def root():
    return {"message": "Video Analysis API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}