import pytest
from app.services.document_checker import DocumentChecker
from fastapi import UploadFile
import io


@pytest.fixture
def checker():
    return DocumentChecker()


def create_mock_file(filename: str, size: int = 1024) -> UploadFile:
    content = b"0" * size
    file = io.BytesIO(content)
    return UploadFile(filename=filename, file=file)


@pytest.mark.asyncio
async def test_federal_package_rejected_missing_docs(checker):
    files = []
    status, issues, docs = await checker.check(files, "federal")
    assert status == "rejected"
    error_messages = [i.message for i in issues]
    assert any("Отсутствует документ" in m for m in error_messages)


@pytest.mark.asyncio
async def test_invalid_file_format(checker):
    files = [create_mock_file("test.txt")]
    status, issues, docs = await checker.check(files, "federal")
    assert any("Недопустимый формат" in i.message for i in issues)


@pytest.mark.asyncio
async def test_unknown_filename_warning(checker):
    files = [create_mock_file("random_photo.png")]
    status, issues, docs = await checker.check(files, "federal")
    assert any(i.level == "warning" for i in issues)


@pytest.mark.asyncio
async def test_regional_package_logic(checker):
    files = [create_mock_file("contract.pdf")]
    status, issues, docs = await checker.check(files, "regional")
    assert status in ["approved", "rejected"]
    assert any(d.detected_type == "contract" for d in docs)


@pytest.mark.asyncio
async def test_file_size_limit_exceeded(checker):
    large_file = create_mock_file("doc.pdf", size=25 * 1024 * 1024)
    files = [large_file]
    status, issues, docs = await checker.check(files, "federal")
    assert any("превышает 20 МБ" in i.message for i in issues)


@pytest.mark.asyncio
async def test_all_documents_provided(checker):
    files = [
        create_mock_file("contract.pdf"),
        create_mock_file("specification.pdf"),
        create_mock_file("act.pdf"),
        create_mock_file("invoice.pdf")
    ]
    status, issues, docs = await checker.check(files, "federal")
    assert status == "approved"
    assert len(docs) == 4
