"""Настройки приложения через pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    default_currency: str = "USD"
    default_hotel_per_day: float = 100.0
    default_food_per_day: float = 50.0
    max_days: int = 30
    app_host: str = "0.0.0.0"
    app_port: int = 8000


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
