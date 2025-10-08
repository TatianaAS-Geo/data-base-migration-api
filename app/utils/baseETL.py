
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from typing import Any, Dict, List, Type
from dateutil import parser

from app.models import CSVUploadResponse  

class BaseETL:
    def __init__(self, db: Session, schema: Dict[str, Any], model_class: Type, file_name: str):
        """
        db: sesión de base de datos de SQLAlchemy
        schema: definición del esquema en formato JSON (con TABLE, PRIMARY_KEY, COLUMNS)
        model_class: modelo SQLAlchemy correspondiente a la tabla
        """
        self.db = db
        self.schema = schema
        self.model_class = model_class
        self.file_name = file_name

    def validate_file(self, file_name: str) -> None:
        """Validar que el archivo sea CSV"""
        if not file_name.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="File must be a CSV file"
            )

    def clean_value(self, x):
        """Convierte NaN en None"""
        if pd.isna(x):
            return None
        return x

    def parse_datetime(self, datetime_str):
        """Parsea string ISO a datetime"""
        if pd.isna(datetime_str):
            return None
        try:
            return parser.isoparse(str(datetime_str))
        except ValueError:
            return None  

    # UPSERT
   
    def get_update_fields(self, stmt):
        """Genera dinámicamente los campos a actualizar en caso de conflicto"""
        update_fields = {}
        primary_keys = set(self.schema.get("PRIMARY_KEY", []))

        for col in self.schema["COLUMNS"].keys():
            if col not in primary_keys:
                update_fields[col] = getattr(stmt.excluded, col)

        update_fields["file_origin_name"] = stmt.excluded.file_origin_name
        update_fields["updated_at"] = func.now()

        return update_fields

    def upsert(self, data: List[Dict[str, Any]], table: Type, index_elements: List[str]):
        """Inserta o actualiza registros en caso de conflicto"""
        stmt = insert(table).values(data)
        stmt = stmt.on_conflict_do_update(
            index_elements=index_elements,
            set_=self.get_update_fields(stmt)
        )
        self.db.execute(stmt)
        self.db.commit()
        return stmt

    def process_csv(self, df: pd.DataFrame, file_name: str) -> CSVUploadResponse:
        """Procesa un DataFrame con base en el esquema"""
        columns = self.schema.get("COLUMNS", {})
        data_list = []
        errors = []

        for index, row in df.iterrows():
            try:
                record = {}
                for col, col_type in columns.items():
                    value = row[col]

                    if col_type.upper() == "INTEGER":
                        record[col] = self.clean_value(float(value))
                    elif col_type.upper() == "FLOAT":
                        record[col] = self.clean_value(float(value))
                    elif col_type.upper() == "STRING":
                        record[col] = self.clean_value(str(value))
                    elif col_type.upper() == "DATETIME":
                        record[col] = self.clean_value(self.parse_datetime(value))
                    else:
                        record[col] = self.clean_value(value)

                record['file_origin_name'] = file_name
                data_list.append(record)

            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                continue

        # UPSERT 
        processed_rows = len(data_list)
        if processed_rows > 0:
            self.upsert(data_list, self.model_class, self.schema["PRIMARY_KEY"])

        return CSVUploadResponse(
            success=True,
            message=f"Successfully processed {processed_rows} records",
            file_name=file_name,
            total_rows=len(df),
            processed_rows=processed_rows,
            errors=errors if errors else None
        )

