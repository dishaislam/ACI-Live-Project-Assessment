from fastapi import UploadFile, HTTPException
import os
import uuid
from pathlib import Path
from typing import Optional

# Configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# Create upload directory if it doesn't exist
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

async def save_uploaded_image(
    file: UploadFile,
    user_id: int,
    session_id: int
) -> str:

    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()  # Get position (file size)
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create user-specific directory structure
    user_dir = Path(UPLOAD_DIR) / str(user_id) / str(session_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Full path to save file
    file_path = user_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    
    return str(file_path)

def delete_session_images(user_id: int, session_id: int):

    session_dir = Path(UPLOAD_DIR) / str(user_id) / str(session_id)
    
    if session_dir.exists():
        import shutil
        shutil.rmtree(session_dir)

def get_image_url(image_path: str) -> str:

    return f"/api/images/{image_path.replace(UPLOAD_DIR + '/', '')}"