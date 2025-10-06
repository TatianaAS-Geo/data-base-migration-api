from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

import pandas as pd

from ..models import Department, DepartmentCreate, CSVUploadResponse
from ..database import get_db, Department

import io


router = APIRouter()
router = APIRouter(tags = ['departments'])

@router.post("/upload/departments", response_model=CSVUploadResponse)
async def upload_departments_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process departments CSV file"""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="File must be a CSV file"
            )
        
        # Read CSV content
        content = await file.read()
        columns_names = ['id', 'department']
        df = pd.read_csv(io.StringIO(content.decode('utf-8')), header=None, names=columns_names)
        
        # Process data
        processed_count = 0
        errors = []
        
        departments_data = []
        for index, row in df.iterrows():
            try:
                departments_data.append({
                    'id': int(row['id']),
                    'department': str(row['department']),
                    'file_origin_name': file.filename
                })
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                continue

        # UPSERT masivo
        if departments_data:
            stmt = insert(Department).values(departments_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_=dict(
                    department=stmt.excluded.department,
                    file_origin_name=stmt.excluded.file_origin_name,
                    updated_at=func.now()
                )
            )
            db.execute(stmt)
            db.commit()
            processed_count = len(departments_data)
        
        return CSVUploadResponse(
            success=True,
            message=f"Successfully processed {processed_count} departments",
            file_name=file.filename,
            total_rows=len(df),
            processed_rows=processed_count,
            errors=errors if errors else None
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing departments CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/get/departments")
async def get_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all departments with pagination"""
    departments = db.query(Department).offset(skip).limit(limit).all()
    return departments