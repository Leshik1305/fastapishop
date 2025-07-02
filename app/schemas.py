from datetime import datetime
from enum import IntEnum
from typing import List

from pydantic import BaseModel, Field
from pydantic.v1 import PositiveInt


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int


class UpdateProduct(CreateProduct):
    grade: float
    all_rewies: List[int]


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None = None


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class GradeEnum(IntEnum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5


class CreateComment(BaseModel):
    comment: str
    product_id: int
    comment_date: datetime = Field(default_factory=datetime.utcnow)
    grade: GradeEnum = GradeEnum.five
    # grade: PositiveInt | None = Field(default= None, ge=1, le=5)  Или так лучше?
