from typing import Any
from pydantic import BaseModel


class BaseMessage(BaseModel):
    content: str
    role: str

    def __init__(self, content: str, role: str):
        super().__init__(content=content, role=role)

    def dict(self, *args: Any, **kwargs: Any) -> dict[str, str]:
        return {"role": self.role, "content": self.content}

class SystemMessage(BaseMessage):
    def __init__(self, content: str):
        super().__init__(content=content, role="system")


class UserMessage(BaseMessage):
    def __init__(self, content: str):
        super().__init__(content=content, role="user")


class AssistantMessage(BaseMessage):
    def __init__(self, content: str):
        super().__init__(content=content, role="assistant")
