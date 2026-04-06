from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./finance.db", alias="DATABASE_URL")


settings = Settings()
