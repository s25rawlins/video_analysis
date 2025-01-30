import whisper
import logging
from pathlib import Path
import tempfile
import boto3
from typing import Optional, Tuple
import os
from app.core.config import settings
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    """Custom exception for transcription-related errors"""
    pass


class TranscriptionService:
    def __init__(self):
        try:
            logger.info("Initializing Whisper model...")
            self.model = whisper.load_model("base")
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            logger.info("TranscriptionService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TranscriptionService: {str(e)}")
            raise TranscriptionError(f"Service initialization failed: {str(e)}")

    async def download_from_s3(self, s3_url: str) -> Tuple[Path, str]:
        """
        Download video from S3 to temporary file
        Returns: Tuple of (file_path, content_type)
        """
        bucket = settings.AWS_BUCKET_NAME
        key = None  # Initialize outside try block

        try:
            logger.info(f"Downloading video from S3: {s3_url}")

            # Extract key from the full URL
            # From: https://ai-video-analysis-dev.s3.us-east-1.amazonaws.com/videos/test_video.mp4
            # We need: videos/test_video.mp4
            key = s3_url.split('.com/')[1]

            logger.info(f"Attempting to access - Bucket: {bucket}, Key: {key}")

            # Create temp file with unique name
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_path = Path(temp_file.name)

            # Download the file
            self.s3_client.download_file(bucket, key, str(temp_path))

            # Get content type
            response = self.s3_client.head_object(Bucket=bucket, Key=key)
            content_type = response.get('ContentType', 'video/mp4')

            logger.info(f"Successfully downloaded video to {temp_path}")
            return temp_path, content_type

        except ClientError as e:
            logger.error(f"S3 error downloading video: {str(e)}")
            logger.error(f"Attempted with bucket: {bucket}, key: {key}")
            raise TranscriptionError(f"Failed to download video: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error downloading video: {str(e)}")
            raise TranscriptionError(f"Download failed: {str(e)}")

    async def transcribe_video(self, video_path: Path) -> dict:
        """
        Transcribe video file using Whisper with detailed output
        """
        try:
            logger.info(f"Starting transcription for {video_path}")

            if not video_path.exists():
                raise TranscriptionError(f"Video file not found: {video_path}")

            # Use Whisper with word timestamps
            result = self.model.transcribe(
                str(video_path),
                word_timestamps=True,
                verbose=True
            )

            # Structure the output
            transcription_details = {
                "text": result["text"],
                "segments": []
            }

            # Process segments with word-level details
            for segment in result["segments"]:
                segment_data = {
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"],
                    "confidence": segment.get("confidence", 0.0),
                    "words": segment.get("words", [])
                }
                transcription_details["segments"].append(segment_data)

            logger.info("Transcription completed successfully with timestamps")
            return transcription_details

        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise TranscriptionError(f"Transcription failed: {str(e)}")

    async def cleanup_temp_file(self, temp_path: Path) -> None:
        """Safely clean up temporary file"""
        try:
            if temp_path.exists():
                os.unlink(temp_path)
                logger.info(f"Cleaned up temporary file: {temp_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {temp_path}: {str(e)}")

    async def process_video(self, s3_url: str) -> str:
        """
        Main processing function: download, transcribe, and cleanup
        """
        temp_path = None
        try:
            # Download video from S3
            temp_path, content_type = await self.download_from_s3(s3_url)

            # Verify it's a video file
            if not content_type.startswith('video/'):
                raise TranscriptionError(f"Invalid content type: {content_type}")

            # Transcribe
            transcription = await self.transcribe_video(temp_path)

            return transcription

        except TranscriptionError:
            raise  # Re-raise our custom exceptions
        except Exception as e:
            logger.error(f"Unexpected error in process_video: {str(e)}")
            raise TranscriptionError(f"Processing failed: {str(e)}")
        finally:
            # Cleanup in finally block to ensure it runs even if errors occur
            if temp_path:
                await self.cleanup_temp_file(temp_path)