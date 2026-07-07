from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MU_API_KEY: Optional[str] = None
    GRSAI_API_KEY: Optional[str] = None
    GRSAI_BASE_URL: str = "https://grsaiapi.com"
    PROVIDER: str = "muapi"
    ALLOW_ORIGINS: str = "*"
    MU_API_BASE: str = "https://api.muapi.ai"
    
    class Config:
        env_file = ".env"

settings = Settings()
