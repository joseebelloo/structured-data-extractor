from pydantic import BaseModel, ConfigDict, Field


class ExtractRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    text: str = Field(min_length=1, max_length=10_000)


class ExtractionResult(BaseModel):
    title: str
    category: str
    provider: str | None
    price: str | None
    summary: str
