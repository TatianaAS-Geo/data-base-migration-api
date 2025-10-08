from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
import io
import logging
import json

from ..models import Job, CSVUploadResponse
from ..database import get_db, Job
from ..utils.baseETL import BaseETL

# Configurar logger
logger = logging.getLogger(__name__)

router = APIRouter(tags=['jobs'])


@router.post("/upload/jobs", response_model=CSVUploadResponse)
async def upload_departments_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    with open('app/table_definitions/jobs.json') as f:
        schema = json.load(f)

    try:
        
        basefunction = BaseETL(db, schema, Job, file.filename)
        validate_file = basefunction.validate_file(file.filename)

        content = await file.read()
        columns_names = schema.get('COLUMNS', {}).keys()

        with pd.read_csv(io.StringIO(content.decode('utf-8')), 
        chunksize=1000,
        header=None, 
        names=columns_names) as reader:
            for chunk in reader:
                df = pd.DataFrame(chunk)
                result = basefunction.process_csv(df, file.filename)
        return result
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing departments CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/get/jobs")
async def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all departments with pagination"""
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return jobs