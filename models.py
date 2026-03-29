from sqlalchemy import Column, Integer, Float
from database import Base

class LogDB(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    mood = Column(Integer)
    sleep = Column(Float)
    work_hours = Column(Float)
    screen_time = Column(Float)