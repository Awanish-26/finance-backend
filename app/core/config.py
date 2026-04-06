from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(
        default="Finance Dashboard Backend", alias="APP_NAME")
    env: str = Field(default="dev", alias="ENV")
    secret_key: str = Field(
        default="change-this-secret-key", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(
        default=120, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    database_url: str = Field(
        default="sqlite:///./finance.db", alias="DATABASE_URL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
