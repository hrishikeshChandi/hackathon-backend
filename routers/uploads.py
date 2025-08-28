import os
from fastapi import HTTPException, status, File, UploadFile, APIRouter
from fastapi.responses import FileResponse
from typing import List, Optional
from utilities.upload_utilities import cleanup, check_uploads, save_files
from utilities.scraper_utilities import price_comp
from utilities.driver import get_driver
from config.constants import FOLDER, REPORT_FILE_NAME

router = APIRouter()

IMAGE_FILE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff"]
AUDIO_FILE_EXTENSIONS = ["mp3", "wav", "aac", "flac", "ogg", "m4a", "wma"]


@router.post("/image_upload", status_code=status.HTTP_201_CREATED)
async def image_upload(
    diet: str,
    symptoms: str,
    current_medicines: str,
    exercise: str,
    additional_info: Optional[str] = None,
    files: List[UploadFile] = File(...),
):

    check_uploads(files, IMAGE_FILE_EXTENSIONS, file_type="image")

    try:
        save_files(files)
        # to be implemented
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Please try again.",
        )
    finally:
        cleanup()


@router.post("/audio_upload", status_code=status.HTTP_201_CREATED)
async def audio_upload(
    diet: str,
    symptoms: str,
    current_medicines: str,
    exercise: str,
    additional_info: Optional[str] = None,
    files: List[UploadFile] = File(...),
):
    check_uploads(files, AUDIO_FILE_EXTENSIONS, file_type="audio")

    try:
        save_files(files)
        # to be implemented
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Please try again.",  # or Internal Server Error
        )
    finally:
        cleanup()


@router.get("/download", status_code=status.HTTP_200_OK)
async def download():
    path = os.path.join(FOLDER, REPORT_FILE_NAME)
    if os.path.exists(path):
        return FileResponse(filename=REPORT_FILE_NAME, path=path)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Please upload image or audio files to get a report.",
        )
