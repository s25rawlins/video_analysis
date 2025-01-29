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