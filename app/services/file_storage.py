from pathlib import Path
import shutil

from fastapi import UploadFile


class FileStorage:
    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    async def save(
        self,
        check_id: int,
        file: UploadFile,
    ) -> str:
        """
        Сохраняет файл на диск и возвращает путь до него.
        """

        check_dir = self.storage_dir / str(check_id)
        check_dir.mkdir(parents=True, exist_ok=True)

        file_path = check_dir / file.filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        await file.seek(0)

        return str(file_path)

    def delete_check_files(
        self,
        check_id: int,
    ) -> None:
        """
        Удаляет все файлы конкретной проверки.
        """

        check_dir = self.storage_dir / str(check_id)

        if check_dir.exists():
            shutil.rmtree(check_dir)
