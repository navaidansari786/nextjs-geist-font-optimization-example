from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class FileUploadResponse(BaseModel):
    id: str
    filename: str
    size: int
    upload_time: datetime
    status: str

class CSVInfo(BaseModel):
    filename: str
    rows: int
    columns: int
    column_names: List[str]
    data_types: Dict[str, str]
    missing_values: Dict[str, int]
    memory_usage: str
    file_size: str

class CSVPreview(BaseModel):
    headers: List[str]
    rows: List[List[Any]]
    total_rows: int
    preview_rows: int

class ScriptExecutionRequest(BaseModel):
    script: str
    input_files: List[str]
    output_filename: str

class ScriptExecutionResponse(BaseModel):
    job_id: str
    status: str
    output_file: Optional[str] = None
    logs: List[str]
    error: Optional[str] = None

class FileListResponse(BaseModel):
    files: List[FileUploadResponse]
    total_count: int
