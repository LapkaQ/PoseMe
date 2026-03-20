from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "PoseMe"
    PROJECT_DESCRIPTION: str = "AI-powered pose estimation application"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    OLLAMA_URL: str
    LLM_MODEL_NAME: str
    GMAIL_USER: str
    GMAIL_PASSWORD: str

    class Config:
        env_file = "../.env"


settings = Settings()