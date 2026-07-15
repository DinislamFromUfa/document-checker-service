from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.check_service import CheckService


def get_check_service(
    session: AsyncSession = Depends(get_db_session),
) -> CheckService:
    return CheckService(session)