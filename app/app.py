# filename: app.py
from fastapi import FastAPI, File, UploadFile
import easyocr
import uvicorn
import re
import json
import tempfile
from PIL import Image
import os
from ultralytics import YOLO
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Get the absolute path to the project's root directory
# Assuming 'app' directory is in the project's root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Construct the absolute path to the model
YOLO_MODEL_PATH = os.path.join(PROJECT_ROOT, "runs", "detect", "train5", "weights", "best.pt")

# Load models
try:
    reader = easyocr.Reader(['en', 'bn'], gpu=False)
    if not os.path.exists(YOLO_MODEL_PATH):
        raise FileNotFoundError(f"YOLO model not found at {YOLO_MODEL_PATH}")
    model = YOLO(YOLO_MODEL_PATH)
    logger.info("Models loaded successfully.")
except Exception as e:
    logger.error(f"Error loading models: {e}")
    # Exit if models can't be loaded
    exit()

def extract_info(text):
    info = {
        'full_name': re.search(r'Name[:\s]+([^\n]+)', text, re.IGNORECASE),
        'nid_number': re.search(r'NID\s*NO[:\s]+([\d]+)', text, re.IGNORECASE),
        'date_of_birth': re.search(r'Date of Birth[:\s]+([^\n]+)', text, re.IGNORECASE),
        'father_name': re.search(r'Father Name[:\s]+([^\n]+)', text, re.IGNORECASE),
        'mother_name': re.search(r'Mother Name[:\s]+([^\n]+)', text, re.IGNORECASE),
        'address': re.search(r'Address[:\s]+([^\n]+(?:\n(?!Issue Date)[^\n]+)*)', text, re.IGNORECASE),
        'issue_date': re.search(r'Issue Date[:\s]+([^\n]+)', text, re.IGNORECASE),
    }
    
    # Clean up extracted data
    for key, value in info.items():
        if value:
            # For address, replace newlines with spaces
            if key == 'address':
                info[key] = ' '.join(value.group(1).strip().split('\n'))
            else:
                info[key] = value.group(1).strip()
        else:
            info[key] = None
            
    return info

@app.post("/extract-nid")
async def extract_nid(file: UploadFile = File(...)):
    try:
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
            shutil.copyfileobj(file.file, temp)
            temp_path = temp.name

        # Open the image
        img = Image.open(temp_path)

        # Run YOLO detection
        results = model(img)

        # Process detections
        if results and len(results[0].boxes) > 0:
            # Assuming the largest detected box is the NID card
            largest_box = max(results[0].boxes, key=lambda box: box.xywh[0][2] * box.xywh[0][3])
            box = largest_box.xyxy[0].cpu().numpy()

            # Crop the image to the detected bounding box
            cropped_img = img.crop(box)
            
            # Save the cropped image to a temporary file to pass to easyocr
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as cropped_temp:
                cropped_img.save(cropped_temp.name)
                cropped_temp_path = cropped_temp.name

            # Perform OCR on the cropped image
            result = reader.readtext(cropped_temp_path)
            text_block = '\n'.join([res[1] for res in result])
            
            # Clean up temporary cropped file
            os.unlink(cropped_temp_path)
        else:
            # If no detection, perform OCR on the whole image
            result = reader.readtext(temp_path)
            text_block = '\n'.join([res[1] for res in result])

        # Clean up temporary uploaded file
        os.unlink(temp_path)

        # Parse the extracted text
        parsed_data = extract_info(text_block)

        return parsed_data

    except Exception as e:
        logger.error(f"Error during NID extraction: {e}")
        return {"error": "Failed to extract information from the NID card."}

# To run the app:
# uvicorn app:app --reload
