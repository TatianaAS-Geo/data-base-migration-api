from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

import pandas as pd

from ..models import Job, JobCreate, CSVUploadResponse
from ..database import get_db, Job

import io


router = APIRouter()
router = APIRouter(tags = ['jobs'])

@router.post("/upload/jobs", response_model=CSVUploadResponse)
async def upload_jobs_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process jobs CSV file"""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="File must be a CSV file"
            )
        
        # Read CSV content
        content = await file.read()
        columns_names = ['id', 'job']
        df = pd.read_csv(io.StringIO(content.decode('utf-8')), header=None, names=columns_names)
        
        # Process data
        processed_count = 0
        errors = []
        
        jobs_data = []
        for index, row in df.iterrows():
            try:
                jobs_data.append({
                    'id': int(row['id']),
                    'job': str(row['job']),
                    'file_origin_name': file.filename
                })
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                continue

        # UPSERT 
        if jobs_data:
            stmt = insert(Job).values(jobs_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_=dict(
                    job=stmt.excluded.job,
                    file_origin_name=stmt.excluded.file_origin_name,
                    updated_at=func.now()
                )
            )
            db.execute(stmt)
            db.commit()
            processed_count = len(jobs_data)
        
        return CSVUploadResponse(
            success=True,
            message=f"Successfully processed {processed_count} jobs",
            file_name=file.filename,
            total_rows=len(df),
            processed_rows=processed_count,
            errors=errors if errors else None
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing jobs CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/get/jobs")
async def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all jobs with pagination"""
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return jobs