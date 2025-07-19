from fastapi import APIRouter, HTTPException
from services.csv_analyzer import CSVAnalyzer
from models.schemas import CSVInfo, CSVPreview
import os

router = APIRouter(prefix="/api/process", tags=["process"])

UPLOAD_DIR = "backend/uploads"

@router.get("/files/{file_id}/info", response_model=CSVInfo)
async def get_file_info(file_id: str):
    """Get detailed information about a CSV file."""
    try:
        # Find the file
        file_path = None
        for filename in os.listdir(UPLOAD_DIR):
            if filename.startswith(f"{file_id}_"):
                file_path = os.path.join(UPLOAD_DIR, filename)
                break
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Analyze the CSV
        info = CSVAnalyzer.analyze_csv(file_path)
        return info
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing file: {str(e)}"
        )

@router.get("/files/{file_id}/preview", response_model=CSVPreview)
async def get_file_preview(file_id: str, max_rows: int = 100):
    """Get a preview of the CSV file."""
    try:
        # Find the file
        file_path = None
        for filename in os.listdir(UPLOAD_DIR):
            if filename.startswith(f"{file_id}_"):
                file_path = os.path.join(UPLOAD_DIR, filename)
                break
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Get preview
        preview = CSVAnalyzer.get_preview(file_path, max_rows)
        return preview
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting file preview: {str(e)}"
        )

@router.get("/files/{file_id}/column/{column_name}/stats")
async def get_column_stats(file_id: str, column_name: str):
    """Get statistics for a specific column."""
    try:
        # Find the file
        file_path = None
        for filename in os.listdir(UPLOAD_DIR):
            if filename.startswith(f"{file_id}_"):
                file_path = os.path.join(UPLOAD_DIR, filename)
                break
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Get column stats
        stats = CSVAnalyzer.get_column_stats(file_path, column_name)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting column stats: {str(e)}"
        )

@router.get("/files/{file_id}/columns")
async def get_columns(file_id: str):
    """Get all column names from a CSV file."""
    try:
        # Find the file
        file_path = None
        for filename in os.listdir(UPLOAD_DIR):
            if filename.startswith(f"{file_id}_"):
                file_path = os.path.join(UPLOAD_DIR, filename)
                break
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Read CSV and get columns
        import pandas as pd
        df = pd.read_csv(file_path)
        
        return {
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting columns: {str(e)}"
        )
