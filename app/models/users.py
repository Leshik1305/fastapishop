from sqlalchemy.orm import relationship

from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_supplier = Column(Boolean, default=False)
    is_customer = Column(Boolean, default=True)

    comments = relationship(
        "Comment",
        back_populates="users",
        uselist=True,
    )
