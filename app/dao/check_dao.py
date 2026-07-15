import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dao.base_dao import BaseDAO
from app.models.check import Check, Document, DocumentVersion


class CheckDAO(BaseDAO[Check]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Check)

    async def get_by_id(self, obj_id: uuid.UUID) -> Check | None:
        result = await self.session.execute(
            select(Check)
            .options(
                selectinload(Check.documents).selectinload(Document.versions)
            )
            .where(Check.id == obj_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = (
            select(
                Check,
                func.count(Document.id).label("document_count")
            )
            .outerjoin(Document)
            .group_by(Check.id)
        )
        
        result = await self.session.execute(stmt)
        checks_data = []
        for check, count in result.all():
            check_dict = {
                "id": check.id,
                "created_at": check.created_at,
                "program": check.program,
                "status": check.status.value,
                "document_count": count
            }
            checks_data.append(check_dict)
            
        return checks_data


class DocumentDAO(BaseDAO[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)

    async def create_version(
        self,
        version: DocumentVersion,
    ) -> DocumentVersion:
        self.session.add(version)
        await self.session.flush()
        await self.session.refresh(version)
        return version