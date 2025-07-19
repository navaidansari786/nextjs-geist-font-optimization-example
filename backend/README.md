# CSV Data Processing Backend

This is the Python FastAPI backend for the CSV data processing application.

## Features
- Upload multiple CSV files
- Analyze CSV files (data types, missing values, statistics)
- Execute Python scripts with pandas operations
- Download processed results

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The server will start on http://localhost:8001

## API Endpoints

### File Upload
- `POST /api/upload/files` - Upload CSV files
- `GET /api/upload/files` - List uploaded files

### File Processing
- `GET /api/process/files/{file_id}/info` - Get CSV file info
- `GET /api/process/files/{file_id}/preview` - Get CSV preview
- `GET /api/process/files/{file_id}/column/{column_name}/stats` - Get column stats

### Script Execution
- `POST /api/scripts/execute` - Execute Python script
- `GET /api/scripts/jobs/{job_id}` - Get job status
- `GET /api/scripts/templates` - Get script templates
- `GET /api/scripts/download/{job_id}/{filename}` - Download result

## Directory Structure
```
backend/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── models/
│   └── schemas.py         # Pydantic models
├── services/
│   ├── csv_analyzer.py    # CSV analysis service
│   └── script_executor.py # Script execution service
├── routers/
│   ├── upload.py          # File upload endpoints
│   ├── process.py         # File processing endpoints
│   └── scripts.py         # Script execution endpoints
├── uploads/               # Uploaded files
└── outputs/               # Processed output files
