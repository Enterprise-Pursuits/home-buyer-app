from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
import csv, io
from fastapi.responses import StreamingResponse
from ..database import get_db
from ..models import Homebuyer
from ..schemas import HomebuyerOut, PaginatedResponse

router = APIRouter(prefix="/api/homebuyers", tags=["homebuyers"])

def build_query(db, county, city, zip_code, date_from, date_to, price_min, price_max, buyer_name):
    q = db.query(Homebuyer)
    if county:      q = q.filter(Homebuyer.county.in_(county))
    if city:        q = q.filter(Homebuyer.city.ilike(f"%{city}%"))
    if zip_code:    q = q.filter(Homebuyer.zip_code == zip_code)
    if date_from:   q = q.filter(Homebuyer.sale_date >= date_from)
    if date_to:     q = q.filter(Homebuyer.sale_date <= date_to)
    if price_min is not None: q = q.filter(Homebuyer.sale_price >= price_min)
    if price_max is not None: q = q.filter(Homebuyer.sale_price <= price_max)
    if buyer_name:  q = q.filter(Homebuyer.buyer_name.ilike(f"%{buyer_name}%"))
    return q

@router.get("/", response_model=PaginatedResponse)
def list_homebuyers(
    county: Optional[List[str]] = Query(None),
    city: Optional[str] = Query(None),
    zip_code: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    buyer_name: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    q = build_query(db, county, city, zip_code, date_from, date_to, price_min, price_max, buyer_name)
    total = q.count()
    results = q.order_by(Homebuyer.sale_date.desc()).offset(skip).limit(limit).all()
    return {"total": total, "results": results}

@router.get("/export/csv")
def export_csv(
    county: Optional[List[str]] = Query(None),
    city: Optional[str] = Query(None),
    zip_code: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    buyer_name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    q = build_query(db, county, city, zip_code, date_from, date_to, price_min, price_max, buyer_name)
    rows = q.order_by(Homebuyer.sale_date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID","Buyer Name","Property Address","City","ZIP","County",
                     "Sale Date","Sale Price","Phone","Email","Mailing Address",
                     "Seller","Parcel ID","Source"])
    for r in rows:
        writer.writerow([r.id, r.buyer_name, r.property_addr, r.city, r.zip_code,
                         r.county, r.sale_date, r.sale_price, r.phone, r.email,
                         r.mailing_addr, r.grantor, r.parcel_id, r.source])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=homebuyers_export.csv"}
    )

@router.get("/{record_id}", response_model=HomebuyerOut)
def get_homebuyer(record_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    record = db.query(Homebuyer).filter(Homebuyer.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Record {record_id} not found")
    return record
