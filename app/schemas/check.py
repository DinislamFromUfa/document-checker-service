from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProgramType(str, Enum):
    FEDERAL = "federal"
    REGIONAL = "regional"


class CreateCheckRequest(BaseModel):
    program: ProgramType = Field(..., description="Программа поддержки")


class DocumentSchema(BaseModel):
    filename: str = Field(validation_alias="original_filename")
    detected_type: Optional[str] = None
    size_kb: int

    model_config = ConfigDict(from_attributes=True)


class IssueSchema(BaseModel):
    level: str
    message: str


class CheckResponse(BaseModel):
    check_id: int = Field(validation_alias="id")
    status: str
    status_label: str
    reason: Optional[str] = None
    issues: List[IssueSchema]
    documents: List[DocumentSchema]
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckListResponse(BaseModel):
    id: int
    created_at: datetime
    program: str
    status: str
    document_count: int

    model_config = ConfigDict(from_attributes=True)


class CheckDetailResponse(CheckResponse):
    id: int
