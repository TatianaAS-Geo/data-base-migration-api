from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from .routers import departments, jobs, employees
from .database import create_tables

import logging

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Database Migration API",
    description="REST API for migrating historical data from CSV files to PostgreSQL",
    version="1.0.0"
)
app.include_router(departments.router)
app.include_router(jobs.router)
app.include_router(employees.router)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("Database tables created successfully")


@app.get("/")
async def root():
    return {"message": "Database Migration API is running"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
