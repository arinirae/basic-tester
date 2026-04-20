from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional


class FieldSchema(BaseModel):
    name: str
    label: Optional[str] = None
    type: str = "text"
    required: bool = False
    placeholder: Optional[str] = None
    options: List[str] = Field(default_factory=list)


class TestScenario(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    target_url: str
    schema_json: str = "[]"
    requires_login: bool = False
    login_url: Optional[str] = None
    login_username_field: Optional[str] = None
    login_email_field: Optional[str] = None
    login_password_field: Optional[str] = None
    login_username: Optional[str] = None
    login_email: Optional[str] = None
    login_password: Optional[str] = None

    class Config:
        extra = "ignore"
