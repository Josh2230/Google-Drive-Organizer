from pydantic import BaseModel
from datetime import datetime


class DriveFile(BaseModel):
    id: str
    name: str
    createdTime: datetime
    modifiedTime: datetime
