"""
Public Records Scraper — NWA Homebuyer Tracker

Data Sources (all public record / ethical):
  - Arkansas GIS Office county deed records: https://www.arcgis.com/
  - Arkansas Assessment Coordination Division: https://www.arkansas.gov/acd/
  - Individual county assessor APIs (free registration required per county)

To activate live data:
  1. Register for a county assessor API key (free)
  2. Add COUNTY_API_KEY to your .env file
  3. Uncomment the live fetch section below

Demo mode uses generated mock data so the app runs without an API key.
"""

import os
import time
import random
import logging
from datetime import date, timedelta
from .database import SessionLocal
from .models import Homebuyer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COUNTY_API_KEY = os.getenv("COUNTY_API_KEY")
COUNTY_API_URL = os.getenv("COUNTY_API_URL", "")  # Set to your county assessor API endpoint

NWA_COUNTIES = [
    "Benton", "Washington", "Boone", "Carroll", "Madison",
    "Newton", "Crawford", "Franklin", "Johnson", "Logan",
    "Sebastian", "Yell", "Scott"
]

NWA_CITIES = {
    "Benton":     ["Bentonville", "Rogers", "Bella Vista", "Pea Ridge", "Siloam Springs"],
    "Washington": ["Fayetteville", "Springdale", "Prairie Grove", "Elkins"],
    "Boone":      ["Harrison", "Jasper"],
    "Carroll":    ["Berryville", "Eureka Springs"],
    "Madison":    ["Huntsville", "Kingston"],
    "Crawford":   ["Van Buren", "Alma"],
    "Sebastian":  ["Fort Smith", "Greenwood"],
    "Franklin":   ["Ozark", "Charleston"],
    "Johnson":    ["Clarksville"],
    "Logan":      ["Paris", "Booneville"],
    "Newton":     ["Jasper"],
    "Yell":       ["Danville", "Dardanelle"],
    "Scott":      ["Waldron"],
}

STREET_NAMES = [
    "Oak", "Maple", "Pine", "Cedar", "Elm", "Walnut", "Cherry",
    "Birch", "Willow", "Magnolia", "Hickory", "Sycamore", "Poplar"
]
STREET_TYPES = ["St", "Ave", "Dr", "Blvd", "Ln", "Ct", "Way", "Rd"]
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "William", "Barbara", "David", "Susan", "Richard", "Jessica",
    "Joseph", "Sarah", "Thomas", "Karen", "Charles", "Lisa"
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Wilson", "Taylor", "Anderson", "Thomas", "Jackson", "White",
    "Harris", "Martin", "Thompson", "Robinson", "Clark", "Lewis"
]


def fetch_from_county_api(county: str) -> list:
    """
    Fetch deed transfer records from county assessor API.
    Requires COUNTY_API_KEY and COUNTY_API_URL in .env.

    Returns list of dicts with keys:
      buyer_name, property_addr, city, zip_code, sale_date,
      sale_price, parcel_id, grantor, phone, email
    """
    if not COUNTY_API_KEY or not COUNTY_API_URL:
        logger.info(f"No county API key configured — using demo data for {county}")
        return []

    # --- LIVE FETCH (uncomment and adapt to your county API) ---
    # import requests
    # response = requests.get(
    #     COUNTY_API_URL,
    #     params={"county": county, "api_key": COUNTY_API_KEY, "type": "deed_transfer"},
    #     timeout=30
    # )
    # if response.status_code == 200:
    #     return response.json().get("records", [])
    # logger.warning(f"County API returned {response.status_code} for {county}")
    return []


def generate_demo_record(county: str) -> dict:
    """Generate a realistic mock record for demo/testing purposes."""
    city = random.choice(NWA_CITIES.get(county, ["Unknown"]))
    number = random.randint(100, 9999)
    street = f"{number} {random.choice(STREET_NAMES)} {random.choice(STREET_TYPES)}"
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    days_ago = random.randint(1, 90)
    sale_date = date.today() - timedelta(days=days_ago)
    price = random.randint(150000, 750000)
    zip_code = str(random.randint(72700, 72999))
    parcel_id = f"{county[:3].upper()}-{random.randint(10000, 99999)}-{random.randint(100, 999)}"

    return {
        "buyer_name":    f"{first} {last}",
        "property_addr": street,
        "city":          city,
        "zip_code":      zip_code,
        "county":        county,
        "sale_date":     sale_date,
        "sale_price":    price,
        "parcel_id":     parcel_id,
        "grantor":       f"{random.choice(LAST_NAMES)} Family Trust",
        "phone":         None,
        "email":         None,
        "source":        "demo_data",
    }


def run_scraper(demo_mode: bool = None):
    """
    Main scraper entry point.

    If COUNTY_API_KEY is set: fetches live public deed records.
    Otherwise: runs in demo mode and generates sample data.
    """
    db = SessionLocal()
    added = 0
    skipped = 0

    live_mode = bool(COUNTY_API_KEY and COUNTY_API_URL)
    if demo_mode is not None:
        live_mode = not demo_mode

    mode_label = "LIVE (county API)" if live_mode else "DEMO (mock data)"
    logger.info(f"Starting scraper in {mode_label} mode")

    for county in NWA_COUNTIES:
        logger.info(f"Processing county: {county}")

        if live_mode:
            records = fetch_from_county_api(county)
        else:
            # Generate 3-8 demo records per county
            records = [generate_demo_record(county) for _ in range(random.randint(3, 8))]

        for rec in records:
            # Skip duplicates by parcel ID
            existing = db.query(Homebuyer).filter(
                Homebuyer.parcel_id == rec["parcel_id"]
            ).first()
            if existing:
                skipped += 1
                continue

            homebuyer = Homebuyer(
                buyer_name=rec.get("buyer_name", ""),
                property_addr=rec.get("property_addr", ""),
                city=rec.get("city", ""),
                zip_code=rec.get("zip_code", ""),
                county=rec.get("county", county),
                sale_date=rec.get("sale_date", date.today()),
                sale_price=rec.get("sale_price", 0),
                parcel_id=rec.get("parcel_id", ""),
                grantor=rec.get("grantor", ""),
                phone=rec.get("phone"),
                email=rec.get("email"),
                source=rec.get("source", "county_records"),
            )
            db.add(homebuyer)
            db.commit()
            added += 1
            logger.info(f"  Saved: {homebuyer.buyer_name} | {homebuyer.property_addr}")

        time.sleep(0.5)

    db.close()
    logger.info(f"Done. Added: {added} | Skipped (duplicates): {skipped}")
    return {"added": added, "skipped": skipped}


if __name__ == "__main__":
    run_scraper()
