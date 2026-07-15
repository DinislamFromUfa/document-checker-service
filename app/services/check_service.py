from typing import Sequence

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.check_dao import CheckDAO, DocumentDAO
from app.models.check import (
    Check,
    CheckStatus,
    Document,
    DocumentVersion,
)
from app.schemas.check import CheckDetailResponse, DocumentSchema, IssueSchema
from app.services.document_checker import DocumentChecker
from app.services.file_storage import FileStorage


STATUS_LABELS: dict[CheckStatus, str] = {
    CheckStatus.PENDING: "Проверка выполняется",
    CheckStatus.APPROVED: "Можно заявлять в банк",
    CheckStatus.REJECTED: "Нельзя заявлять в банк",
}


class CheckService:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.check_dao = CheckDAO(session)
        self.document_dao = DocumentDAO(session)

        self.document_checker = DocumentChecker()
        self.file_storage = FileStorage()

    async def process_package(
        self,
        files: Sequence[UploadFile],
        program: str,
    ):
        try:
            result_status, issues, documents = await (
                self.document_checker.check(
                    files=files,
                    program=program,
                )
            )

            check_status = self._resolve_status(result_status)

            check = await self._create_check(
                program=program,
                status=check_status,
                issues=issues,
            )

            await self._save_documents(
                check_id=check.id,
                files=files,
                documents=documents,
            )

            await self.session.commit()

            return CheckResponse(
                check_id=check.id,
                status=check.status.value,
                status_label=STATUS_LABELS[check.status],
                reason=check.reason,
                issues=issues,
                documents=documents,
                checked_at=check.checked_at,
            )

        except Exception:
            await self.session.rollback()
            raise

    async def get_all_checks(self):
        return await self.check_dao.get_all()

    async def get_check_by_id(self, check_id: int) -> CheckDetailResponse | None:
        check = await self.check_dao.get_by_id(check_id)
        if not check:
            return None

        return CheckDetailResponse(
            id=check.id,
            status=check.status.value,
            status_label=STATUS_LABELS[check.status],
            reason=check.reason,
            issues=[IssueSchema(level=i['level'], message=i['message']) for i in check.issues],
            documents=[
                DocumentSchema(
                    filename=doc.original_filename,
                    detected_type=doc.doc_type,
                    size_kb=doc.size_kb
                ) for doc in check.documents
            ],
            checked_at=check.checked_at
        )

    @staticmethod
    def _resolve_status(
        checker_status: str,
    ) -> CheckStatus:
        if checker_status == CheckStatus.APPROVED.value:
            return CheckStatus.APPROVED

        return CheckStatus.REJECTED

    async def _create_check(
        self,
        program: str,
        status: CheckStatus,
        issues,
    ) -> Check:
        check = Check(
            program=program,
            status=status,
            reason=(
                "Обнаружены ошибки при проверке документов"
                if status == CheckStatus.REJECTED
                else None
            ),
            issues=[
                issue.model_dump()
                for issue in issues
            ],
        )

        await self.check_dao.create(check)

        return check

    async def _save_documents(
        self,
        check_id: int,
        files: Sequence[UploadFile],
        documents,
    ) -> None:
        for upload_file, document_schema in zip(
            files,
            documents,
        ):
            document = Document(
                check_id=check_id,
                original_filename=document_schema.filename,
                doc_type=document_schema.detected_type,
                size_kb=document_schema.size_kb,
            )

            await self.document_dao.create(document)

            file_path = await self.file_storage.save(
                check_id,
                upload_file,
            )

            version = DocumentVersion(
                document_id=document.id,
                version_number=1,
                file_path=file_path,
                extracted_data=None,
            )

            await self.document_dao.create_version(version)