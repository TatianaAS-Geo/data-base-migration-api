from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

import pandas as pd
from datetime import datetime

from ..models import Employee, EmployeeCreate, CSVUploadResponse
from ..database import get_db, Employee

import io
import logging


# Configurar logger para este módulo
logger = logging.getLogger(__name__)

router = APIRouter()
router = APIRouter(tags = ['employees'])

@router.post("/upload/employees", response_model=CSVUploadResponse)
async def upload_employees_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process employees CSV file"""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="File must be a CSV file"
            )
        
        # Read CSV content
        content = await file.read()
        columns_names = ['id', 'name', 'datetime_str', 'department_id', 'job_id']
        df = pd.read_csv( io.StringIO(content.decode('utf-8')), 
                header=None, 
                names=columns_names
            )
        df = df.where(pd.notnull(df), None)
        # Process data
        processed_count = 0
        errors = []
        
        employees_data = []
        for index, row in df.iterrows():
            try:
                employees_data.append({
                    'id': int(row['id']),
                    'name': str(row['name']),
                    'datetime_str':  str(row['datetime_str']),
                    'department_id': int(row['department_id']),
                    'job_id': int(row['job_id']),
                    'file_origin_name': file.filename
                })
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                continue

        # UPSERT masivo
        if employees_data:
            stmt = insert(Employee).values(employees_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_=dict(
                    name=stmt.excluded.name,
                    datetime=stmt.excluded.datetime,
                    department_id=stmt.excluded.department_id,
                    job_id=stmt.excluded.job_id,
                    file_origin_name=stmt.excluded.file_origin_name,
                    updated_at=func.now()
                )
            )
            db.execute(stmt)
            db.commit()
            processed_count = len(employees_data)
        
        return CSVUploadResponse(
            success=True,
            message=f"Successfully processed {processed_count} employees",
            file_name=file.filename,
            total_rows=len(df),
            processed_rows=processed_count,
            errors=errors if errors else None
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing employees CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/get/employees")
async def get_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all employees with pagination"""
    employees = db.query(Employee).offset(skip).limit(limit).all()
    return employees