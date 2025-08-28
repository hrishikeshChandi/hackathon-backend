import os, shutil
from fastapi import HTTPException, status, UploadFile
from typing import List
from config.constants import FOLDER, REPORT_FILE_NAME


def check_uploads(
    files: List[UploadFile], file_extensions: list, file_type: str
) -> None:
    for file in files:
        if (
            "." not in file.filename
            or file.filename.rsplit(".")[-1].lower() not in file_extensions
        ):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Only {file_type} files are allowed",
            )


def save_files(files: List[UploadFile]) -> None:
    if not os.path.exists(FOLDER):
        os.mkdir(FOLDER)

    file_paths = []

    for file in files:
        path = os.path.join(FOLDER, file.filename)
        print(f"added : {path}")
        file_paths.append(path)

        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)


def cleanup() -> None:
    if os.path.exists(FOLDER):
        current_files = os.listdir(FOLDER)

        if REPORT_FILE_NAME in current_files:
            current_files.remove(REPORT_FILE_NAME)

        if len(current_files):
            for file_name in current_files:
                path = os.path.join(FOLDER, file_name)
                os.remove(path)
