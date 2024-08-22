from pydantic import BaseModel
from typing import List

class Character(BaseModel):
    name: str
    imageUrl: str

class ImageRequest(BaseModel):
    studentTaskId: int
    characters: List[Character]
