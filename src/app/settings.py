import os
from functools import cache as cache_func

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT: str = os.environ.get('BOT_API_TOKEN')
    EXTERNAL_API_URL: str = os.environ.get('EXTERNAL_API_URL')
    EXTERNAL_API_CHECK_ACCESS: str = os.environ.get('EXTERNAL_API_CHECK_ACCESS')


@cache_func
def get_settings() -> Settings:
    return Settings()


settings = get_settings()