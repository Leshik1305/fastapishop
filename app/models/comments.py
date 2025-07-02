from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship

from app.backend.db import Base


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    comment = Column(Text)
    comment_date = Column(
        DateTime(timezone=True), default=datetime.utcnow, server_default=func.now()
    )
    grade = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)

    products = relationship(
        "Product",
        back_populates="comments",
        uselist=False,
    )
    users = relationship(
        "User",
        back_populates="comments",
        uselist=False,
    )
