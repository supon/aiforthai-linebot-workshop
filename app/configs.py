from pydantic_settings import BaseSettings


class Configs(BaseSettings):
    AIFORTHAI_APIKEY: str
    LINE_CHANNEL_ACCESS_TOKEN: str
    LINE_CHANNEL_SECRET:str      