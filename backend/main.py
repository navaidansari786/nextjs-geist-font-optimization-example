from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers.upload import router as upload_router
from routers.process import router as process_router
from routers.scripts import router as scripts_router
import os
import sys

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create FastAPI app
app = FastAPI(
    title="CSV Data Processing API",
    description="API for uploading, analyzing, and processing CSV files with Python scripts",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("backend/uploads", exist_ok=True)
os.makedirs("backend/outputs", exist_ok=True)

# Mount static files for downloads
app.mount("/api/download", StaticFiles(directory="backend/outputs"), name="download")

# Include routers
app.include_router(upload_router)
app.include_router(process_router)
app.include_router(scripts_router)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "CSV Data Processing API",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "CSV Data Processing API is running",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
