import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
import logging
from typing import Optional
from fastapi import UploadFile

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.AWS_BUCKET_NAME

    async def upload_video(self, file: UploadFile) -> Optional[str]:
        """
        Upload a video file to S3 and return its URL
        """
        try:
            file_content = await file.read()
            object_key = f"videos/{file.filename}"

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_content,
                ContentType=file.content_type
            )

            url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{object_key}"
            return url

        except ClientError as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {str(e)}")
            return None