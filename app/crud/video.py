from sqlalchemy.orm import Session
from app.models.video import Video, ProcessingStatus
from datetime import datetime
from typing import Optional

class VideoRepository:
    @staticmethod
    async def create_video(
        db: Session,
        filename: str,
        s3_url: str,
        created_by: Optional[str] = None
    ) -> Video:
        video = Video(
            filename=filename,
            s3_url=s3_url,
            status=ProcessingStatus.UPLOADED,
            upload_time=datetime.utcnow(),
            created_by=created_by
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        return video

    @staticmethod
    async def update_transcription(
            db: Session,
            video_id: int,
            transcription_details: dict
    ) -> Optional[Video]:
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.transcription = transcription_details["text"]  # Keep original field
            video.transcription_details = transcription_details  # Add detailed data
            video.status = ProcessingStatus.COMPLETED
            video.processed_time = datetime.utcnow()
            db.commit()
            db.refresh(video)
        return video