from apscheduler.schedulers.background import BackgroundScheduler
from .scraper import run_scraper

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_scraper, "cron", hour=7, minute=0, id="daily_scrape")
    scheduler.start()
    return scheduler
