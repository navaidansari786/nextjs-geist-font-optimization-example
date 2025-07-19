from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
from datetime import datetime
from typing import List
from models.schemas import FileUploadResponse, FileListResponse

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Ensure upload directory exists
UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/files", response_model=List[FileUploadResponse])
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload multiple CSV files."""
    uploaded_files = []
    
    for file in files:
        # Validate file extension
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is not a CSV file"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        try:
            contents = await file.read()
            with open(file_path, 'wb') as f:
                f.write(contents)
            
            file_info = FileUploadResponse(
                id=file_id,
                filename=file.filename,
                size=len(contents),
                upload_time=datetime.now(),
                status="uploaded"
            )
            
            uploaded_files.append(file_info)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading file {file.filename}: {str(e)}"
            )
    
    return uploaded_files

@router.get("/files", response_model=FileListResponse)
async def list_files():
    """List all uploaded files."""
    files = []
    
    try:
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith('.csv'):
                file_path = os.path.join(UPLOAD_DIR, filename)
                file_stats = os.stat(file_path)
                
                # Extract original filename from stored filename
                parts = filename.split('_', 1)
                original_filename = parts[1] if len(parts) > 1 else filename
                
                file_info = FileUploadResponse(
                    id=parts[0],
                    filename=original_filename,
                    size=file_stats.st_size,
                    upload_time=datetime.fromtimestamp(file_stats.st_mtime),
                    status="uploaded"
                )
                
                files.append(file_info)
        
        return FileListResponse(files=files, total_count=len(files))
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing files: {str(e)}"
        )

@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a specific file."""
    try:
        for filename in os.listdir(UPLOAD_DIR):
            if filename.startswith(f"{file_id}_"):
                file_path = os.path.join(UPLOAD_DIR, filename)
                os.remove(file_path)
                return {"message": "File deleted successfully"}
        
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {str(e)}"
        )

@router.get("/files/{file_id}/download")
async def download_file(file_id: str):
    """Download a specific file."""
    try:
        for filename in os.listdir(UPLOAD_DIR):
            if filename.startswith(f"{file_id}_"):
                file_path = os.path.join(UPLOAD_DIR, filename)
                parts = filename.split('_', 1)
                original_filename = parts[1] if len(parts) > 1 else filename
                
                return FileResponse(
                    file_path,
                    media_type='text/csv',
                    filename=original_filename
                )
        
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading file: {str(e)}"
        )
