from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class HomebuyerBase(BaseModel):
    buyer_name:    str
    property_addr: str
    city:          str
    zip_code:      str
    county:        str
    sale_date:     date
    sale_price:    Optional[float] = None
    parcel_id:     Optional[str]   = None
    grantor:       Optional[str]   = None
    phone:         Optional[str]   = None
    email:         Optional[str]   = None
    mailing_addr:  Optional[str]   = None
    source:        Optional[str]   = None

class HomebuyerCreate(HomebuyerBase):
    pass

class HomebuyerOut(HomebuyerBase):
    id:          int
    skip_traced: bool
    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    total:   int
    results: List[HomebuyerOut]
