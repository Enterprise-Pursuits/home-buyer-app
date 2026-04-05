from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class Homebuyer(Base):
    __tablename__ = "homebuyers"
    id            = Column(Integer, primary_key=True, index=True)
    buyer_name    = Column(String, index=True)
    property_addr = Column(String)
    city          = Column(String, index=True)
    zip_code      = Column(String, index=True)
    county        = Column(String, index=True)
    sale_date     = Column(Date, index=True)
    sale_price    = Column(Float, index=True)
    parcel_id     = Column(String, unique=True, index=True)
    grantor       = Column(String)
    phone         = Column(String, nullable=True)
    email         = Column(String, nullable=True)
    mailing_addr  = Column(String, nullable=True)
    skip_traced   = Column(Boolean, default=False)
    source        = Column(String)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

