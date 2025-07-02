from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship

from app.backend.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Integer)
    image_url = Column(String)
    stock = Column(Integer)
    supplier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    rating = Column(Float)
    is_active = Column(Boolean, default=True)
    sum_rewies = Column(Integer, default=0)
    count_rewies = Column(Integer, default=0)

    category = relationship(
        "Category",
        back_populates="products",
        uselist=False,
    )
    comments = relationship(
        "Comment",
        back_populates="products",
        uselist=True,
    )
