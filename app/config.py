import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Label Padhega India Backend"
    api_v1_str: str = "/api/v1"
    
    # IBM Cloud Credentials
    ibm_api_key: str = ""
    ibm_service_url: str = ""
    project_id: str = ""
    
    # Watson Discovery / OCR
    watson_discovery_api_key: str = ""
    watson_discovery_url: str = ""
    discovery_environment_id: str = ""
    discovery_collection_id: str = ""
    
    # Server default
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields in .env

@lru_cache()
def get_settings():
    return Settings()
