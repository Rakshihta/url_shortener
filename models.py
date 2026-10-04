from database import Base, declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Date

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key = True)
    email = Column(String)
    hashed_password = Column(String)

class Link(Base):
    __tablename__ = "link"
    id = Column(Integer, primary_key=True)
    short_code = Column(String, unique=True, index=True)
    long_url = Column(String)
    created_at = Column(Date)
    clicks = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=True) 
    