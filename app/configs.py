from pydantic_settings import BaseSettings, SettingsConfigDict


class Configs(BaseSettings):
    AIFORTHAI_APIKEY: str
    LINE_CHANNEL_ACCESS_TOKEN: str
    LINE_CHANNEL_SECRET: str

    # Basic NLP VARIABLES
    WAV_URL: str
    WAV_FILE: str
    DIR_FILE: str
    URL_PARTII: str
    URL_VAJA: str

    # Image VARIABLES
    URL_MAEWMONG: str
    IMG_RESULT: str
    URL_PERSON_DETEC: str
    URL_CAPGEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore",str_strip_whitespace=True)
