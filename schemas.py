from pydantic import BaseModel, ConfigDict

class URLCreate(BaseModel):
    original_url: str

class URLOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    original_url: str
    clicks: int