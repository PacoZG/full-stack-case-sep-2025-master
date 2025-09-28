from typing import List
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlmodel import select

from app.core.config import settings
# from app.core.security import get_current_active_superuser # Removed superuser dependency
from app.models import UploadedFile, SignalMeasurement
from app.api.deps import get_db
from app.services.signal_parser import process_signal_file

router = APIRouter(tags=["signal-data"])

@router.post("/upload-signal-data", response_model=UploadedFile)
async def upload_signal_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_active_superuser), # Removed superuser dependency
):
    """
    Uploads a signal data file (CSV or binary) for processing.
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file name provided.")

    # Determine file type (a more robust check would be needed for production)
    file_type = "csv" if file.filename.lower().endswith(".csv") else "binary"

    # Save metadata to UploadedFile table
    uploaded_file_obj = UploadedFile(
        id=uuid.uuid4(),
        filename=file.filename,
        upload_timestamp=datetime.utcnow(),
        status="pending",
        file_type=file_type,
    )
    db.add(uploaded_file_obj)
    db.commit()
    db.refresh(uploaded_file_obj)

    # Read file content
    file_content = await file.read()

    # Add the processing task to background tasks
    background_tasks.add_task(
        process_signal_file,
        file_content,
        file_type,
        uploaded_file_obj.id,
        db # Pass the session to the background task
    )

    return uploaded_file_obj

@router.get("/uploaded-files", response_model=List[UploadedFile])
async def get_uploaded_files(
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_active_superuser),
):
    """
    Retrieves a list of all uploaded signal data files.
    """
    uploaded_files = db.exec(select(UploadedFile)).all()
    return uploaded_files

@router.get("/uploaded-files/{file_id}", response_model=UploadedFile)
async def get_uploaded_file(
    file_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieves details and status of a single uploaded file.
    """
    uploaded_file = db.get(UploadedFile, file_id)
    if not uploaded_file:
        raise HTTPException(status_code=404, detail="File not found")
    return uploaded_file
