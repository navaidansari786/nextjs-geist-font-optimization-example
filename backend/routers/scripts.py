from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.script_executor import ScriptExecutor
from models.schemas import ScriptExecutionRequest, ScriptExecutionResponse
import os
import uuid
from typing import List, Dict

router = APIRouter(prefix="/api/scripts", tags=["scripts"])

# In-memory job storage (in production, use Redis or database)
job_status = {}

@router.post("/execute", response_model=ScriptExecutionResponse)
async def execute_script(request: ScriptExecutionRequest, background_tasks: BackgroundTasks):
    """Execute a Python script with provided CSV files."""
    job_id = str(uuid.uuid4())
    
    # Validate input files
    for file_path in request.input_files:
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"Input file not found: {file_path}"
            )
    
    # Initialize job status
    job_status[job_id] = {
        "status": "processing",
        "logs": [],
        "output_file": None,
        "error": None
    }
    
    # Execute script in background
    background_tasks.add_task(
        process_script,
        job_id,
        request.script,
        request.input_files,
        request.output_filename
    )
    
    return ScriptExecutionResponse(
        job_id=job_id,
        status="processing",
        logs=[],
        output_file=None,
        error=None
    )

@router.get("/jobs/{job_id}", response_model=ScriptExecutionResponse)
async def get_job_status(job_id: str):
    """Get the status of a script execution job."""
    if job_id not in job_status:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    job = job_status[job_id]
    return ScriptExecutionResponse(
        job_id=job_id,
        status=job["status"],
        logs=job["logs"],
        output_file=job["output_file"],
        error=job["error"]
    )

@router.get("/templates")
async def get_script_templates():
    """Get available script templates."""
    return ScriptExecutor.get_script_templates()

@router.get("/download/{job_id}/{filename}")
async def download_result(job_id: str, filename: str):
    """Download the result file from a completed job."""
    if job_id not in job_status:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    job = job_status[job_id]
    if job["status"] != "completed" or not job["output_file"]:
        raise HTTPException(
            status_code=404,
            detail="Result file not available"
        )
    
    if not os.path.exists(job["output_file"]):
        raise HTTPException(
            status_code=404,
            detail="Result file not found"
        )
    
    from fastapi.responses import FileResponse
    
    return FileResponse(
        job["output_file"],
        media_type='text/csv',
        filename=filename
    )

def process_script(job_id: str, script_content: str, input_files: List[str], output_filename: str):
    """Process the script execution in background."""
    try:
        result = ScriptExecutor.execute_script(script_content, input_files, output_filename)
        
        # Update job status
        job_status[job_id].update({
            "status": result["status"],
            "logs": result["logs"],
            "output_file": result["output_file"],
            "error": result["error"]
        })
        
    except Exception as e:
        job_status[job_id].update({
            "status": "failed",
            "logs": [str(e)],
            "output_file": None,
            "error": str(e)
        })

@router.get("/jobs")
async def list_jobs():
    """List all jobs (for debugging)."""
    return {"jobs": list(job_status.keys())}

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job from status tracking."""
    if job_id in job_status:
        del job_status[job_id]
        return {"message": "Job deleted"}
    
    raise HTTPException(
        status_code=404,
        detail="Job not found"
    )
