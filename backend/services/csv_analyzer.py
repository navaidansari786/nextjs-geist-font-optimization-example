import pandas as pd
import os
from typing import Dict, List, Any
from models.schemas import CSVInfo, CSVPreview

class CSVAnalyzer:
    @staticmethod
    def analyze_csv(file_path: str) -> CSVInfo:
        """Analyze CSV file and return detailed information."""
        try:
            df = pd.read_csv(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Analyze data types
            data_types = {}
            for col in df.columns:
                dtype = str(df[col].dtype)
                if dtype == 'int64':
                    data_types[col] = 'integer'
                elif dtype == 'float64':
                    data_types[col] = 'float'
                elif dtype == 'object':
                    if df[col].str.match(r'\d{4}-\d{2}-\d{2}').all():
                        data_types[col] = 'date'
                    else:
                        data_types[col] = 'string'
                elif dtype == 'bool':
                    data_types[col] = 'boolean'
                else:
                    data_types[col] = dtype
            
            # Count missing values
            missing_values = df.isnull().sum().to_dict()
            
            # Memory usage
            memory_usage = f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
            file_size_str = f"{file_size / 1024:.2f} KB" if file_size < 1024*1024 else f"{file_size / 1024**2:.2f} MB"
            
            return CSVInfo(
                filename=os.path.basename(file_path),
                rows=len(df),
                columns=len(df.columns),
                column_names=list(df.columns),
                data_types=data_types,
                missing_values=missing_values,
                memory_usage=memory_usage,
                file_size=file_size_str
            )
            
        except Exception as e:
            raise Exception(f"Error analyzing CSV: {str(e)}")
    
    @staticmethod
    def get_preview(file_path: str, max_rows: int = 100) -> CSVPreview:
        """Get a preview of the CSV file."""
        try:
            df = pd.read_csv(file_path)
            
            # Limit to max_rows for preview
            preview_df = df.head(max_rows)
            
            return CSVPreview(
                headers=list(preview_df.columns),
                rows=preview_df.values.tolist(),
                total_rows=len(df),
                preview_rows=len(preview_df)
            )
            
        except Exception as e:
            raise Exception(f"Error getting CSV preview: {str(e)}")
    
    @staticmethod
    def get_column_stats(file_path: str, column: str) -> Dict[str, Any]:
        """Get statistics for a specific column."""
        try:
            df = pd.read_csv(file_path)
            
            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found")
            
            col_data = df[column]
            stats = {
                'column': column,
                'dtype': str(col_data.dtype),
                'null_count': col_data.isnull().sum(),
                'unique_count': col_data.nunique()
            }
            
            if pd.api.types.is_numeric_dtype(col_data):
                stats.update({
                    'min': col_data.min(),
                    'max': col_data.max(),
                    'mean': col_data.mean(),
                    'median': col_data.median(),
                    'std': col_data.std()
                })
            elif pd.api.types.is_object_dtype(col_data):
                stats.update({
                    'most_common': col_data.mode().iloc[0] if not col_data.mode().empty else None,
                    'least_common': col_data.value_counts().index[-1] if len(col_data.value_counts()) > 0 else None
                })
            
            return stats
            
        except Exception as e:
            raise Exception(f"Error getting column stats: {str(e)}")
