from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.s3 import S3Service
from app.crud.video import VideoRepository
from app.db.session import get_db
import logging

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_video(
        file: UploadFile = File(...),
        s3_service: S3Service = Depends(S3Service),
        db: Session = Depends(get_db),
):
    """
    Upload a video file and create database record
    """
    if not file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=400,
            detail="File uploaded is not a video"
        )

    try:
        # Upload to S3
        s3_url = await s3_service.upload_video(file)
        if not s3_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload video to storage"
            )

        # Create database record
        video = await VideoRepository.create_video(
            db=db,
            filename=file.filename,
            s3_url=s3_url
        )

        return {
            "id": video.id,
            "filename": video.filename,
            "status": video.status.value,
            "s3_url": video.s3_url
        }

    except Exception as e:
        logger.error(f"Error processing video upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error processing video upload"
        )