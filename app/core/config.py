from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logger = logging.getLogger(__name__)

from pathlib import Path
from dotenv import load_dotenv
from typing import ClassVar, Optional

# Load .env file manually before creating Settings instance
ENV_FILE_PATH = (Path(__file__).resolve().parent.parent / ".env").resolve()

if ENV_FILE_PATH.exists():
    load_dotenv(dotenv_path=ENV_FILE_PATH)
    print(f"✅ .env file loaded from: {ENV_FILE_PATH}")
else:
    print("⚠️ .env file not found!")


class Settings(BaseSettings):
    PROJECT_NAME: str = "Video Analysis Platform"
    API_V1_STR: str = "/api/v1"

    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = ""
    AWS_REGION: str = "us-east-1"

    # Database Configuration
    DATABASE_URL: str = "postgresql://video_user:2501@localhost/video_analysis"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

settings = Settings()