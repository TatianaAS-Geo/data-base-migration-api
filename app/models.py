from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class DepartmentBase(BaseModel):
    id: int
    department: str = Field(..., min_length=1, max_length=100)

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    created_at: datetime
    updated_at: datetime
    file_origin_name: str

    class Config:
        from_attributes = True

class JobBase(BaseModel):
    id: int
    job: str = Field(..., min_length=1, max_length=100)

class JobCreate(JobBase):
    pass

class Job(JobBase):
    created_at: datetime
    updated_at: datetime
    file_origin_name: str

    class Config:
        from_attributes = True

class EmployeeBase(BaseModel):
    id: int
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    datetime_str: Optional[str] = Field(None, description="ISO format datetime string")
    department_id: Optional[int] = Field(None)
    job_id: Optional[int] = Field(None)

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    created_at: datetime
    updated_at: datetime
    file_origin_name: str
    class Config:
        from_attributes = True


class CSVUploadResponse(BaseModel):
    success: bool
    message: str
    file_name: str
    total_rows: int
    processed_rows: int
    errors: Optional[List[str]] = None
