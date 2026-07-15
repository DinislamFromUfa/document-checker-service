from datetime import UTC, datetime
import enum

import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CheckStatus(enum.Enum):
    PENDING = "check_in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"


class Check(Base):
    __tablename__ = "checks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    program: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[CheckStatus] = mapped_column(
        Enum(CheckStatus),
        default=CheckStatus.PENDING,
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    issues: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    documents: Mapped[list["Document"]] = relationship(
        back_populates="check",
        cascade="all, delete-orphan",
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    check_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("checks.id", ondelete="CASCADE"), nullable=False
    )

    original_filename: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    doc_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    size_kb: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    check: Mapped["Check"] = relationship(
        back_populates="documents",
    )

    versions: Mapped[list["DocumentVersion"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )

    version_number: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    extracted_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    document: Mapped["Document"] = relationship(
        back_populates="versions",
    )
