# models.py

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base  # note: no dot

class HitRecord(Base):
    __tablename__ = "hits"

    id = Column(Integer, primary_key=True, index=True)
    hit_id = Column(String(64), unique=True, index=True, nullable=False)
    creator_name = Column(String(255), nullable=False)
    rights_holder_name = Column(String(255), nullable=False)
    identity_type = Column(String(50), nullable=False)
    rights_status = Column(String(20), nullable=False)  # allowed | prohibited | restricted | negotiable
    rights_json = Column(Text, nullable=False)          # raw JSON string
    sha256 = Column(String(64), index=True, nullable=False)
    blake3 = Column(String(64), index=True, nullable=False)
    source_filename = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
