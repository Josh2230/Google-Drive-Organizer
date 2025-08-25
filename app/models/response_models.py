from pydantic import BaseModel
from typing import List
from app.models.file_models import DriveFile


class FileListResponse(BaseModel):
    files: List[DriveFile]
