from pathlib import Path

from fastapi import UploadFile

from app.schemas.check import DocumentSchema, IssueSchema


class DocumentChecker:
    MAX_FILE_SIZE_KB = 20 * 1024

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".jpg",
        ".jpeg",
        ".png",
    }

    DOCUMENT_PATTERNS = {
        "contract": [
            "договор",
            "contract",
        ],
        "specification": [
            "спецификация",
            "specification",
            "spec",
        ],
        "invoice": [
            "счет",
            "счёт",
            "invoice",
        ],
        "act": [
            "акт",
            "упд",
            "act",
        ],
    }

    REQUIRED_DOCUMENTS = {
        "federal": {
            "contract",
            "specification",
            "invoice",
            "act",
        },
        "regional": {
            "contract",
            "invoice",
            "act",
        },
    }

    async def check(
        self,
        files: list[UploadFile],
        program: str,
    ) -> tuple[str, list[IssueSchema], list[DocumentSchema]]:

        issues: list[IssueSchema] = []
        documents: list[DocumentSchema] = []
        detected_types: list[str] = []

        for file in files:

            extension = Path(file.filename).suffix.lower()

            if extension not in self.ALLOWED_EXTENSIONS:
                issues.append(
                    IssueSchema(
                        level="error",
                        message=f"Недопустимый формат файла: {file.filename}",
                    )
                )

            content = await file.read()

            size_kb = len(content) // 1024

            if size_kb > self.MAX_FILE_SIZE_KB:
                issues.append(
                    IssueSchema(
                        level="error",
                        message=f"Файл {file.filename} превышает 20 МБ",
                    )
                )

            doc_type = self.detect_document_type(file.filename)

            if doc_type is None:
                issues.append(
                    IssueSchema(
                        level="warning",
                        message=f"Не удалось определить тип документа: {file.filename}",
                    )
                )
            else:
                detected_types.append(doc_type)

            documents.append(
                DocumentSchema(
                    filename=file.filename,
                    detected_type=doc_type,
                    size_kb=size_kb,
                )
            )

            await file.seek(0)

        issues.extend(
            self.validate_package(
                detected_types,
                program,
            )
        )

        status = "approved"

        if any(issue.level == "error" for issue in issues):
            status = "rejected"

        return status, issues, documents

    def detect_document_type(
        self,
        filename: str,
    ) -> str | None:

        filename = filename.lower()

        for doc_type, patterns in self.DOCUMENT_PATTERNS.items():
            if any(pattern in filename for pattern in patterns):
                return doc_type

        return None

    def validate_package(
        self,
        detected_types: list[str],
        program: str,
    ) -> list[IssueSchema]:

        issues: list[IssueSchema] = []

        required = self.REQUIRED_DOCUMENTS.get(program)

        if required is None:
            issues.append(
                IssueSchema(
                    level="error",
                    message=f"Неизвестная программа: {program}",
                )
            )
            return issues

        missing = required - set(detected_types)

        for doc in sorted(missing):
            issues.append(
                IssueSchema(
                    level="error",
                    message=f"Отсутствует документ: {doc}",
                )
            )

        return issues