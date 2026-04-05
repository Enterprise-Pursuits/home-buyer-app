# NWA New Homebuyer Tracker

A full-stack web application that aggregates new homebuyer records across 13 Arkansas counties for sales prospecting and lead management. Built using public county assessor records — fully ethical and compliant with public records law.

---

## What It Does

- **Aggregates** deed transfer records from Arkansas county assessor public data
- **Filters** records by county, city, ZIP, date range, price range, and buyer name
- **Batch imports** records from Excel (.xlsx) and PDF files exported from county websites
- **Exports** filtered results to CSV for use in CRM and dialer tools
- **Auto-syncs** daily via a background scheduler when connected to a county API

---

## Data Sources (Public Record)

All data comes from legally public sources:

| Source | URL | Notes |
|---|---|---|
| Arkansas GIS Office | https://www.geoportal.arkansas.gov | County deed/transfer data |
| Benton County Assessor | https://www.bentoncountyar.gov/assessor | Free API registration |
| Washington County Assessor | https://www.washingtoncoar.gov | Free API registration |
| Arkansas Assessment Coordination | https://www.arkansas.gov/acd | Statewide records |

> **Manual upload option:** If a county doesn't have an API, download their Excel or PDF export and use the Batch Upload feature in the app sidebar.

---

## Features

- Multi-county filter with dropdown selector
- Date range and price range filters
- Buyer name search
- **Batch upload** — drag-and-drop Excel/PDF files from county assessor offices
- Auto-detects column names (flexible header mapping)
- Duplicate detection by parcel ID
- CSV export of any filtered result set
- Daily auto-sync scheduler (when API key configured)
- Demo mode — runs with generated sample data, no API key required

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | React + Tailwind CSS |
| Scheduling | APScheduler |
| PDF Parsing | pdfplumber |
| Excel Parsing | openpyxl |
| Containerization | Docker + Docker Compose |

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Backend

```bash
cd backend
cp .env.example .env        # Add your API keys
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm start                   # Runs on http://localhost:3000
```

### Docker (full stack)

```bash
docker-compose up --build
```

---

## Batch Upload Format

The app accepts Excel and PDF files from county assessor offices. Column names are auto-detected. Supported column variations:

| Field | Accepted Column Names |
|---|---|
| Buyer Name | Buyer Name, Buyer, Name, Grantee, Purchaser |
| Property Address | Property Address, Address, Street Address |
| Sale Date | Sale Date, Date, Date Sold, Closing Date |
| Sale Price | Sale Price, Price, Amount, Purchase Price |
| County | County, County Name |
| Parcel ID | Parcel ID, Parcel Number, Tax ID, Account Number |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
DATABASE_URL=sqlite:///./nwa_homebuyers.db
SECRET_KEY=your-secret-key

# County assessor API (free registration)
COUNTY_API_KEY=
COUNTY_API_URL=

# Skip trace API (optional)
SKIP_TRACE_API_KEY=
```

---

## Author

**AI Solutions Engineer:** Chad Smith, Ed.S.
Built under [Enterprise Pursuits](https://github.com/Enterprise-Pursuits) as part of an AI Solutions Engineer portfolio.

*Uses only publicly available county assessor records. No scraping of private or restricted websites.*
