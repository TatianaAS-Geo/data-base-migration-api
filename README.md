# Database Migration API

A FastAPI-based REST API for migrating historical data from CSV files to PostgreSQL database. This API supports three main entities: departments, jobs, and employees with batch processing capabilities.

## Features

- **CSV File Upload**: Upload and process CSV files for departments, jobs, and employees
- **Batch Operations**: Insert up to 1000 records in a single request
- **Data Validation**: Comprehensive validation using Pydantic models
- **PostgreSQL Integration**: Full database integration with SQLAlchemy ORM
- **Error Handling**: Detailed error reporting and transaction rollback
- **RESTful API**: Clean REST endpoints with automatic documentation

## Prerequisites

- Python 3.8+
- PostgreSQL 12+

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd Database_API
   ```
2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
3. **Set up PostgreSQL database**:

   - Create a new database for the migration
   - Update the database connection string in `env_example.txt` and rename it to `.env`
4. **Run database migration**:

   ```bash
   psql -U username -d migration_db -f migration.sql
   ```

## Configuration

Create a `.env` file based on `env_example.txt`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/migration_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=migration_db
DB_USER=username
DB_PASSWORD=password
```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## API Endpoints

### Health Check

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

### CSV Upload Endpoints

- `POST /upload/departments` - Upload departments CSV file
- `POST /upload/jobs` - Upload jobs CSV file
- `POST /upload/employees` - Upload employees CSV file

### Data Retrieval Endpoints

- `GET /departments` - Get all departments (with pagination)
- `GET /jobs` - Get all jobs (with pagination)
- `GET /employees` - Get all employees (with pagination)

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository or contact the development team.
