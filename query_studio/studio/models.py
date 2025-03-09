import typing as t

from pydantic import BaseModel, Field


class Question(BaseModel):
    question: str = Field(...)
    metadata: t.Dict[str, t.Any] = Field(default_factory=dict)
