"""
schemas.py - the shape of the JSON going in and out of the API (Pydantic).

models.py  = what is stored in the database
schemas.py = what the API accepts (...Create) and returns (...Out)

Keeping them separate means we control exactly what clients can send
and what they get back.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------- Requests (data the client sends) ----------

class QuestionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    text: str = Field(
        min_length=1, max_length=200, examples=["Which topic should we cover next?"]
    )
    options: list[str] = Field(
        min_length=2, max_length=10, examples=[["Databases", "Testing", "Deployment"]]
    )

    @field_validator("options")
    @classmethod
    def options_must_not_be_blank(cls, options: list[str]) -> list[str]:
        cleaned = [option.strip() for option in options if option.strip()]
        if len(cleaned) < 2:
            raise ValueError("Give at least 2 options that are not blank")
        return cleaned


class AnswerCreate(BaseModel):
    option_id: int = Field(examples=[1])


# ---------- Responses (data the API returns) ----------
# from_attributes=True lets Pydantic read SQLAlchemy objects directly,
# so endpoints can simply `return question`.

class OptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    created_at: datetime
    options: list[OptionOut]


class AnswerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    option_id: int
    created_at: datetime


class OptionResult(BaseModel):
    option_id: int
    text: str
    votes: int


class QuestionResults(BaseModel):
    question_id: int
    question: str
    total_votes: int
    results: list[OptionResult]
