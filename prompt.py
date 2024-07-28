from typing import Any
from pydantic import BaseModel, Field


class PromptTemplate(BaseModel):
    template: str = Field(..., description="The template string with placeholders")

    def render(self, **kwargs: Any) -> str:
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing value for {e}")