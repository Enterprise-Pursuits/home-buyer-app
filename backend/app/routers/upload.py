"""
Batch Upload Router — NWA Homebuyer Tracker

Accepts Excel (.xlsx, .xls) and PDF files containing homebuyer records.
Maps columns automatically and imports into the database.

Expected Excel columns (flexible — will match by name):
  Buyer Name, Property Address, City, ZIP, County, Sale Date,
  Sale Price, Phone, Email, Parcel ID, Seller/Grantor
"""

import io
import logging
import re
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Homebuyer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/upload", tags=["upload"])

# Column name aliases — maps variations to our field names
COLUMN_MAP = {
    "buyer_name":    ["buyer name", "buyer", "name", "purchaser", "grantee", "owner"],
    "property_addr": ["property address", "address", "street address", "property addr", "street"],
    "city":          ["city", "municipality"],
    "zip_code":      ["zip", "zip code", "postal code", "zipcode"],
    "county":        ["county", "county name"],
    "sale_date":     ["sale date", "date", "date sold", "closing date", "deed date"],
    "sale_price":    ["sale price", "price", "amount", "purchase price", "sales price"],
    "phone":         ["phone", "phone number", "telephone", "cell", "mobile"],
    "email":         ["email", "email address", "e-mail"],
    "parcel_id":     ["parcel id", "parcel", "parcel number", "tax id", "account number"],
    "grantor":       ["grantor", "seller", "seller name", "previous owner"],
}


def normalize_col(col: str) -> str:
    return col.strip().lower().replace("_", " ").replace("-", " ")


def map_columns(headers: list) -> dict:
    """Map spreadsheet headers to our field names."""
    mapping = {}
    norm_headers = {normalize_col(h): h for h in headers}
    for field, aliases in COLUMN_MAP.items():
        for alias in aliases:
            if alias in norm_headers:
                mapping[field] = norm_headers[alias]
                break
    return mapping


def parse_price(val) -> float:
    if val is None:
        return 0.0
    cleaned = re.sub(r"[^\d.]", "", str(val))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_date(val) -> date:
    if val is None:
        return date.today()
    if isinstance(val, date):
        return val
    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y"]:
        try:
            from datetime import datetime
            return datetime.strptime(str(val).strip(), fmt).date()
        except ValueError:
            continue
    return date.today()


def row_to_homebuyer(row: dict, col_map: dict, source: str) -> Homebuyer:
    def get(field):
        col = col_map.get(field)
        return row.get(col) if col else None

    parcel = str(get("parcel_id") or "").strip()
    if not parcel:
        import time
        addr = str(get("property_addr") or "")[:10].replace(" ", "-")
        parcel = f"UPLOAD-{addr}-{int(time.time())}"

    return Homebuyer(
        buyer_name=str(get("buyer_name") or "").strip(),
        property_addr=str(get("property_addr") or "").strip(),
        city=str(get("city") or "").strip(),
        zip_code=str(get("zip_code") or "").strip(),
        county=str(get("county") or "").strip(),
        sale_date=parse_date(get("sale_date")),
        sale_price=parse_price(get("sale_price")),
        parcel_id=parcel,
        grantor=str(get("grantor") or "").strip(),
        phone=str(get("phone") or "").strip() or None,
        email=str(get("email") or "").strip() or None,
        source=source,
    )


def import_records(records: list, db: Session, source: str) -> dict:
    added = 0
    skipped = 0
    errors = []

    for rec in records:
        if not rec.get("buyer_name") and not rec.get("property_addr"):
            skipped += 1
            continue
        existing = db.query(Homebuyer).filter(
            Homebuyer.parcel_id == rec.get("parcel_id")
        ).first()
        if existing:
            skipped += 1
            continue
        try:
            homebuyer = Homebuyer(
                buyer_name=rec.get("buyer_name", ""),
                property_addr=rec.get("property_addr", ""),
                city=rec.get("city", ""),
                zip_code=rec.get("zip_code", ""),
                county=rec.get("county", ""),
                sale_date=rec.get("sale_date", date.today()),
                sale_price=rec.get("sale_price", 0.0),
                parcel_id=rec.get("parcel_id", ""),
                grantor=rec.get("grantor", ""),
                phone=rec.get("phone") or None,
                email=rec.get("email") or None,
                source=source,
            )
            db.add(homebuyer)
            db.commit()
            added += 1
        except Exception as e:
            db.rollback()
            errors.append(str(e))
            skipped += 1

    return {"added": added, "skipped": skipped, "errors": errors[:10]}


@router.post("/excel")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload an Excel file (.xlsx or .xls) containing homebuyer records."""
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="File must be .xlsx or .xls")

    try:
        import openpyxl
    except ImportError:
        raise HTTPException(status_code=500, detail="openpyxl not installed — run: pip install openpyxl")

    content = await file.read()
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        raise HTTPException(status_code=400, detail="Excel file is empty")

    headers = [str(h) if h else "" for h in rows[0]]
    col_map = map_columns(headers)

    if not col_map:
        raise HTTPException(
            status_code=400,
            detail=f"No recognized columns found. Headers detected: {headers}"
        )

    records = []
    for row in rows[1:]:
        row_dict = dict(zip(headers, row))
        rec = {
            "buyer_name":    str(row_dict.get(col_map.get("buyer_name", ""), "") or "").strip(),
            "property_addr": str(row_dict.get(col_map.get("property_addr", ""), "") or "").strip(),
            "city":          str(row_dict.get(col_map.get("city", ""), "") or "").strip(),
            "zip_code":      str(row_dict.get(col_map.get("zip_code", ""), "") or "").strip(),
            "county":        str(row_dict.get(col_map.get("county", ""), "") or "").strip(),
            "sale_date":     parse_date(row_dict.get(col_map.get("sale_date", ""))),
            "sale_price":    parse_price(row_dict.get(col_map.get("sale_price", ""))),
            "parcel_id":     str(row_dict.get(col_map.get("parcel_id", ""), "") or "").strip(),
            "grantor":       str(row_dict.get(col_map.get("grantor", ""), "") or "").strip(),
            "phone":         str(row_dict.get(col_map.get("phone", ""), "") or "").strip() or None,
            "email":         str(row_dict.get(col_map.get("email", ""), "") or "").strip() or None,
        }
        records.append(rec)

    result = import_records(records, db, source=f"excel_upload:{file.filename}")
    return {
        "message": f"Excel import complete: {file.filename}",
        "columns_detected": list(col_map.keys()),
        **result
    }


@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a PDF containing homebuyer/deed records.
    Best results with structured PDFs from county assessor offices.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a .pdf")

    try:
        import pdfplumber
    except ImportError:
        raise HTTPException(status_code=500, detail="pdfplumber not installed — run: pip install pdfplumber")

    content = await file.read()
    records = []

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            # Try table extraction first (works for structured PDFs)
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    if not table:
                        continue
                    headers = [str(h).strip() if h else "" for h in table[0]]
                    col_map = map_columns(headers)
                    if not col_map:
                        continue
                    for row in table[1:]:
                        if not row or all(cell is None for cell in row):
                            continue
                        row_dict = dict(zip(headers, [str(c).strip() if c else "" for c in row]))
                        rec = {
                            "buyer_name":    row_dict.get(col_map.get("buyer_name", ""), ""),
                            "property_addr": row_dict.get(col_map.get("property_addr", ""), ""),
                            "city":          row_dict.get(col_map.get("city", ""), ""),
                            "zip_code":      row_dict.get(col_map.get("zip_code", ""), ""),
                            "county":        row_dict.get(col_map.get("county", ""), ""),
                            "sale_date":     parse_date(row_dict.get(col_map.get("sale_date", ""))),
                            "sale_price":    parse_price(row_dict.get(col_map.get("sale_price", ""))),
                            "parcel_id":     row_dict.get(col_map.get("parcel_id", ""), ""),
                            "grantor":       row_dict.get(col_map.get("grantor", ""), ""),
                            "phone":         row_dict.get(col_map.get("phone", ""), "") or None,
                            "email":         row_dict.get(col_map.get("email", ""), "") or None,
                        }
                        records.append(rec)

    if not records:
        raise HTTPException(
            status_code=422,
            detail="No table data found in PDF. County assessor PDFs with structured tables work best."
        )

    result = import_records(records, db, source=f"pdf_upload:{file.filename}")
    return {
        "message": f"PDF import complete: {file.filename}",
        "pages_processed": len(pdf.pages) if 'pdf' in dir() else 0,
        **result
    }


@router.post("/batch")
async def upload_batch(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    """Upload multiple Excel and/or PDF files at once."""
    results = []
    for file in files:
        if file.filename.endswith((".xlsx", ".xls")):
            result = await upload_excel(file, db)
        elif file.filename.endswith(".pdf"):
            result = await upload_pdf(file, db)
        else:
            result = {"message": f"Skipped {file.filename} — unsupported format", "added": 0, "skipped": 0}
        results.append(result)

    total_added = sum(r.get("added", 0) for r in results)
    total_skipped = sum(r.get("skipped", 0) for r in results)
    return {"files_processed": len(files), "total_added": total_added, "total_skipped": total_skipped, "details": results}
