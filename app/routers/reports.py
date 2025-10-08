from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from pathlib import Path

from ..database import get_db
from ..models import QuarterlyHiringReport, DepartmentHiringStats

router = APIRouter(tags=['reports'])

@router.get("/reports/quarterly-hiring-sql", response_model=List[QuarterlyHiringReport])
async def get_quarterly_hiring_report_sql(db: Session = Depends(get_db)):
    try:
        # Usar pathlib para una ruta más robusta
        sql_file = Path(__file__).parent.parent / 'table_definitions' / 'quarter_report.sql'
        
        if not sql_file.exists():
            raise HTTPException(status_code=404, detail="SQL file not found")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_query = f.read()
    
        result = db.execute(text(sql_query))
        rows = result.fetchall()
        if not rows:
            return []  # Devolver lista vacía si no hay datos
        
        return [
            QuarterlyHiringReport(
                department=row.department,
                job=row.job,
                Q1=int(row.Q1 or 0),
                Q2=int(row.Q2 or 0),
                Q3=int(row.Q3 or 0),
                Q4=int(row.Q4 or 0)
            )
            for row in rows
        ]
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="SQL file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quarterly report: {str(e)}")


