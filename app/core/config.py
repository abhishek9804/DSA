from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    APP_NAME: str

    APP_ENV: str

    DATABASE_URL: str

    SECRET_KEY: str

    LOG_LEVEL: str

    class Config:
        env_file = ".env"

settings = Settings()