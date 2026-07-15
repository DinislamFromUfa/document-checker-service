from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict


class DocumentSchema(BaseModel):
    filename: str
    detected_type: str | None = None
    size_kb: int

    model_config = ConfigDict(from_attributes=True)


class IssueSchema(BaseModel):
    level: str
    message: str

    model_config = ConfigDict(from_attributes=True)


class CheckListResponse(BaseModel):
    id: int
    created_at: datetime
    program: str
    status: str
    document_count: int

    model_config = ConfigDict(from_attributes=True)


class ExtractedDataSchema(BaseModel):
    contractor: str
    amount: str
    date: str
    subject: str

    model_config = ConfigDict(from_attributes=True)


class CheckDetailResponse(BaseModel):
    check_id: str
    status: str
    status_label: str
    reason: str | None = None
    issues: List[IssueSchema]
    documents: List[DocumentSchema]
    extracted: ExtractedDataSchema | None = None
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)