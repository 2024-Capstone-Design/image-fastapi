from pydantic import BaseModel
from typing import List

class ImageRequestItem(BaseModel):
    name: str
    imageUrl: str
    promptType: str

class ImageRequest(BaseModel):
    studentTaskId: int
    imageRequest: List[ImageRequestItem]