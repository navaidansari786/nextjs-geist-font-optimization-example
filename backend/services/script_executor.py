import subprocess
import tempfile
import os
import json
import sys
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import uuid

class ScriptExecutor:
    @staticmethod
    def execute_script(script_content: str, input_files: List[str], output_filename: str) -> Dict[str, Any]:
        """Execute Python script with provided CSV files."""
        job_id = str(uuid.uuid4())
        logs = []
        
        try:
            # Create temporary directory for execution
            with tempfile.TemporaryDirectory() as temp_dir:
                logs.append(f"Created temporary directory: {temp_dir}")
                
                # Copy input files to temp directory
                input_paths = []
                for file_path in input_files:
                    if os.path.exists(file_path):
                        filename = os.path.basename(file_path)
                        temp_file_path = os.path.join(temp_dir, filename)
                        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
                        os.system(f'cp "{file_path}" "{temp_file_path}"')
                        input_paths.append(temp_file_path)
                        logs.append(f"Copied input file: {filename}")
                
                # Create the script file
                script_path = os.path.join(temp_dir, "script.py")
                with open(script_path, 'w') as f:
                    # Add imports and setup
                    enhanced_script = f"""
import pandas as pd
import numpy as np
import json
import os
import sys

# Setup paths
input_files = {json.dumps([os.path.basename(f) for f in input_paths])}
output_filename = "{output_filename}"

# Load CSV files
dataframes = {{}}
for file in input_files:
    if os.path.exists(file):
        dataframes[file] = pd.read_csv(file)

# Available variables:
# - dataframes: dict mapping filename to pandas DataFrame
# - output_filename: string for output file name

{script_content}

# Save result
if 'result' in locals():
    result.to_csv(output_filename, index=False)
    print(f"Output saved to {{output_filename}}")
else:
    print("No 'result' DataFrame found. Please assign your final DataFrame to a variable named 'result'")
"""
                    f.write(enhanced_script)
                
                logs.append("Script file created")
                
                # Execute the script
                output_file = os.path.join(temp_dir, output_filename)
                result = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir
                )
                
                logs.extend(result.stdout.strip().split('\n') if result.stdout.strip() else [])
                
                if result.stderr:
                    logs.extend([f"ERROR: {line}" for line in result.stderr.strip().split('\n')])
                
                if result.returncode != 0:
                    return {
                        "job_id": job_id,
                        "status": "failed",
                        "logs": logs,
                        "error": result.stderr,
                        "output_file": None
                    }
                
                # Check if output file was created
                if os.path.exists(output_file):
                    # Move output file to permanent location
                    output_dir = "backend/outputs"
                    os.makedirs(output_dir, exist_ok=True)
                    final_output = os.path.join(output_dir, f"{job_id}_{output_filename}")
                    os.system(f'cp "{output_file}" "{final_output}"')
                    
                    logs.append(f"Output file created: {final_output}")
                    
                    return {
                        "job_id": job_id,
                        "status": "completed",
                        "logs": logs,
                        "output_file": final_output,
                        "error": None
                    }
                else:
                    return {
                        "job_id": job_id,
                        "status": "failed",
                        "logs": logs,
                        "error": "Output file was not created",
                        "output_file": None
                    }
                    
        except Exception as e:
            return {
                "job_id": job_id,
                "status": "failed",
                "logs": logs,
                "error": str(e),
                "output_file": None
            }
    
    @staticmethod
    def get_script_templates() -> List[Dict[str, str]]:
        """Get available script templates."""
        return [
            {
                "name": "Basic Data Cleaning",
                "description": "Remove duplicates and handle missing values",
                "template": """# Basic data cleaning
df = dataframes[list(dataframes.keys())[0]]  # Use first file

# Remove duplicates
df = df.drop_duplicates()

# Handle missing values - fill with mean for numeric, mode for categorical
for col in df.columns:
    if df[col].dtype in ['int64', 'float64']:
        df[col] = df[col].fillna(df[col].mean())
    else:
        df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown')

result = df"""
            },
            {
                "name": "Filter Rows",
                "description": "Filter rows based on conditions",
                "template": """# Filter rows example
df = dataframes[list(dataframes.keys())[0]]  # Use first file

# Example: Filter rows where column 'age' > 30
if 'age' in df.columns:
    result = df[df['age'] > 30]
else:
    result = df"""
            },
            {
                "name": "Group By and Aggregate",
                "description": "Group data and calculate aggregates",
                "template": """# Group by and aggregate
df = dataframes[list(dataframes.keys())[0]]  # Use first file

# Example: Group by 'category' and calculate mean of 'value'
if 'category' in df.columns and 'value' in df.columns:
    result = df.groupby('category')['value'].mean().reset_index()
else:
    result = df"""
            },
            {
                "name": "Merge DataFrames",
                "description": "Merge multiple CSV files",
                "template": """# Merge multiple CSV files
if len(dataframes) > 1:
    files = list(dataframes.keys())
    result = dataframes[files[0]]
    
    for file in files[1:]:
        # Example: merge on common column 'id'
        if 'id' in result.columns and 'id' in dataframes[file].columns:
            result = pd.merge(result, dataframes[file], on='id', how='inner')
        else:
            result = pd.concat([result, dataframes[file]], ignore_index=True)
else:
    result = dataframes[list(dataframes.keys())[0]]"""
            }
        ]
