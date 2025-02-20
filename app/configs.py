from pydantic_settings import BaseSettings

class Configs(BaseSettings):
    AIFORTHAI_APIKEY: str
    LINE_CHANNEL_ACCESS_TOKEN: str
    LINE_CHANNEL_SECRET: str
    URL: str
    WAV_FILE: str
    DIR_FILE: str
    URL_VAJA: str
    URL_PARTII: str

    class Config:
        env_file = ".env"  # Ensure it reads from .env file

 