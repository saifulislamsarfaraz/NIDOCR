# filename: app.py
from fastapi import FastAPI, File, UploadFile
import easyocr
import uvicorn
import re
import json
import tempfile
from PIL import Image

from fastapi import FastAPI, File, UploadFile
import easyocr
import re
import tempfile
import shutil
import os
from ultralytics import YOLO
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw

app = FastAPI()
reader = easyocr.Reader(['en', 'bn'], gpu=False)

def extract_info(text):
    info = {
        'full_name': re.search(r'NAME[:\s]*([^\n]+)', text, re.IGNORECASE),
        'nid_number': re.search(r'NID\s*NUMBER[:\s]*([\dA-Z]+)', text, re.IGNORECASE),
        'date_of_birth': re.search(r'DATE\s*OF\s*BIRTH[:\s]*([^\n]+)', text, re.IGNORECASE),
        'place_of_birth': re.search(r'PLACE\s*OF\s*BIRTH[:\s]*([^\n]+)', text, re.IGNORECASE),
        'address': re.search(r'ADDRESS[:\s]*([^\n]+)', text, re.IGNORECASE),
        'issue_date': re.search(r'ISSUE\s*DATE[:\s]*([^\n]+)', text, re.IGNORECASE),
        'expiry_date': re.search(r'EXPIRY\s*DATE[:\s]*([^\n]+)', text, re.IGNORECASE)
    }
    return {k: v.group(1).strip() if v else None for k, v in info.items()}

@app.post("/extract-nid")
async def extract_nid(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        temp.write(await file.read())
        temp.flush()
        result = reader.readtext(temp.name)
        text_block = '\n'.join([res[1] for res in result])
        parsed = extract_info(text_block)
        return parsed

# Run with: uvicorn app:app --reload
yolo_model_path = r"C:\Users\saifu\OneDrive\Desktop\NIDOCR\runs\detect\train5\weights\best.pt"
model = YOLO(yolo_model_path)