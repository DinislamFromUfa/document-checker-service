from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.api.dependencies import get_check_service
from app.schemas.check import (
    CheckDetailResponse,
    CheckListResponse,
    CheckResponse,
)
from app.services.check_service import CheckService


check_router = APIRouter(
    prefix="/checks",
    tags=["Checks"],
)


@check_router.post(
    "",
    response_model=CheckDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_check(
    files: list[UploadFile] = File(...),
    program: str = Form(...),
    service: CheckService = Depends(get_check_service),
):
    return await service.process_package(files, program)


@check_router.get(
    "",
    response_model=list[CheckListResponse],
)
async def get_checks(
    service: CheckService = Depends(get_check_service),
):
    return await service.get_all_checks()


@check_router.get(
    "/{check_id}",
    response_model=CheckDetailResponse,
)
async def get_check_detail(
    check_id: int,
    service: CheckService = Depends(get_check_service),
):
    check = await service.get_check_by_id(check_id)

    if check is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check not found",
        )

    return check