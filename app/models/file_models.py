from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing import List


class DriveFile(BaseModel):
    id: str
    name: str
    createdTime: datetime
    modifiedTime: Optional[datetime] = None
    owners: Optional[List[dict]] = None
