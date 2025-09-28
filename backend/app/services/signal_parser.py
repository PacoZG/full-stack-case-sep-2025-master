import csv
from datetime import datetime
from typing import List, Dict, Any
from io import StringIO
import uuid
import re
import struct
import logging

from sqlalchemy.orm import Session

from app.models import SignalMeasurement, UploadedFile

# Setup logger
logger = logging.getLogger("signal_parser")
handler = logging.FileHandler("signal_parser.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

async def parse_csv_file(
    file_content: str, uploaded_file_id: uuid.UUID, db: Session
) -> List[SignalMeasurement]:
    """
    Parses a CSV file content and extracts signal measurements.
    Handles variations in field names by normalizing headers.
    """
    measurements = []
    csv_reader = csv.DictReader(StringIO(file_content))

    # Field normalization mapping (add more aliases as needed)
    FIELD_ALIASES = {
        "facility_name": ["facility_name", "facility", "plant_name"],
        "facility_section_name": ["facility_section_name", "section", "section_name"],
        "machine_name": ["machine_name", "asset_name", "equipment_name"],
        "measurement_point_name": ["measurement_point_name", "sensor_location", "point_name"],
        "measured_at": ["measured_at", "timestamp", "datetime", "time"],
        "rotating_speed": ["rotating_speed", "speed", "rpm", "frequency"],
        "signal": ["signal", "signal_data", "values"],
        "signal_unit": ["signal_unit", "unit"],
        "sampling_rate_hz": ["sampling_rate_hz", "sampling_rate", "fs"],
    }

    def normalize_row(row):
        norm = {}
        for key, aliases in FIELD_ALIASES.items():
            for alias in aliases:
                if alias in row:
                    norm[key] = row[alias]
                    break
        return norm

    for row in csv_reader:
        try:
            norm_row = normalize_row(row)
            measured_at = datetime.fromisoformat(norm_row["measured_at"]) if "measured_at" in norm_row else None
            # Accept signal as array or string
            signal_val = norm_row.get("signal", "")
            if isinstance(signal_val, str):
                # Remove brackets and split
                signal_str = re.sub(r"[\[\]]", "", signal_val)
                signal_list = [float(x) for x in signal_str.split(",") if x.strip()]
            elif isinstance(signal_val, list):
                signal_list = [float(x) for x in signal_val]
            else:
                signal_list = []
            measurement = SignalMeasurement(
                uploaded_file_id=uploaded_file_id,
                facility_name=norm_row.get("facility_name", ""),
                facility_section_name=norm_row.get("facility_section_name", ""),
                machine_name=norm_row.get("machine_name", ""),
                measurement_point_name=norm_row.get("measurement_point_name", ""),
                measured_at=measured_at,
                rotating_speed=float(norm_row.get("rotating_speed", 0)),
                signal_unit=norm_row.get("signal_unit", ""),
                sampling_rate_hz=float(norm_row.get("sampling_rate_hz", 0)),
                signal=signal_list,
            )
            measurements.append(measurement)
        except Exception as e:
            logger.error(f"Error parsing CSV row: {e}. Row: {row}")
            continue
    logger.info(f"Parsed {len(measurements)} measurements from CSV for file {uploaded_file_id}")
    return measurements

async def parse_binary_file(
    file_content: bytes, uploaded_file_id: uuid.UUID, db: Session
) -> List[SignalMeasurement]:
    """
    Parses a binary file content and extracts signal measurements.
    This implementation assumes a placeholder binary format. Replace with actual format as needed.
    """
    measurements = []
    # Example: Suppose each record is fixed length and fields are packed in order.
    # This is a placeholder. Replace with actual binary format parsing.
    RECORD_SIZE = 256  # Example size, adjust as needed
    offset = 0
    while offset + RECORD_SIZE <= len(file_content):
        record = file_content[offset:offset+RECORD_SIZE]
        try:
            # Unpack fields (example: 64 bytes for facility_name, ...)
            # Example unpacking: adjust struct format and slicing as per real format
            facility_name = record[0:64].decode('utf-8').strip('\x00')
            facility_section_name = record[64:128].decode('utf-8').strip('\x00')
            machine_name = record[128:160].decode('utf-8').strip('\x00')
            measurement_point_name = record[160:192].decode('utf-8').strip('\x00')
            measured_at_ts = struct.unpack('d', record[192:200])[0]  # double, 8 bytes
            measured_at = datetime.utcfromtimestamp(measured_at_ts)
            rotating_speed = struct.unpack('f', record[200:204])[0]  # float, 4 bytes
            signal_unit = record[204:208].decode('utf-8').strip('\x00')
            sampling_rate_hz = struct.unpack('f', record[208:212])[0]
            # Example: next 44 bytes for signal (11 floats)
            signal = list(struct.unpack('11f', record[212:256]))
            measurement = SignalMeasurement(
                uploaded_file_id=uploaded_file_id,
                facility_name=facility_name,
                facility_section_name=facility_section_name,
                machine_name=machine_name,
                measurement_point_name=measurement_point_name,
                measured_at=measured_at,
                rotating_speed=rotating_speed,
                signal_unit=signal_unit,
                sampling_rate_hz=sampling_rate_hz,
                signal=signal,
            )
            measurements.append(measurement)
        except Exception as e:
            logger.error(f"Error parsing binary record at offset {offset}: {e}")
        offset += RECORD_SIZE
    logger.info(f"Parsed {len(measurements)} measurements from binary for file {uploaded_file_id}")
    return measurements

async def process_signal_file(
    file_content: Any, file_type: str, uploaded_file_id: uuid.UUID, db: Session
) -> None:
    """
    Dispatches file content to the appropriate parser and saves measurements to the database.
    """
    measurements: List[SignalMeasurement] = []
    if file_type == "csv":
        measurements = await parse_csv_file(file_content.decode("utf-8"), uploaded_file_id, db)
    elif file_type == "binary":
        measurements = await parse_binary_file(file_content, uploaded_file_id, db)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    if measurements:
        db.add_all(measurements)
        db.commit()
        logger.info(f"Saved {len(measurements)} measurements to DB for file {uploaded_file_id}")
        # Update the status of the uploaded file
        uploaded_file = db.get(UploadedFile, uploaded_file_id)
        if uploaded_file:
            uploaded_file.status = "completed"
            db.add(uploaded_file)
            db.commit()
            db.refresh(uploaded_file)
    else:
        logger.warning(f"No measurements parsed for file {uploaded_file_id} (type: {file_type})")
        # If no measurements were parsed, mark as failed or completed with warnings
        uploaded_file = db.get(UploadedFile, uploaded_file_id)
        if uploaded_file:
            uploaded_file.status = "completed_no_data" # Or "failed"
            db.add(uploaded_file)
            db.commit()
            db.refresh(uploaded_file)
