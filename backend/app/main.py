from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import homebuyers
from .routers import upload
from .scheduler import start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NWA New Homebuyer Tracker", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(homebuyers.router)
app.include_router(upload.router)
scheduler = start_scheduler()

@app.get("/")
def root():
    return {"message": "NWA Homebuyer Tracker API is running", "version": "2.0.0"}

@app.get("/api/counties")
def get_counties():
    return {"counties": [
        "Benton", "Washington", "Boone", "Carroll", "Madison",
        "Newton", "Crawford", "Franklin", "Johnson", "Logan",
        "Sebastian", "Yell", "Scott"
    ]}
