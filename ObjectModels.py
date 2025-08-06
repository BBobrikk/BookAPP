from pydantic import BaseModel, Field


class BookModel(BaseModel):
    title: str
    rating: float = Field(ge=0, le=5)
