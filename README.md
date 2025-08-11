# NID Card OCR Information Extractor

This project is designed to extract information from National ID cards using Optical Character Recognition (OCR). It features a web-based interface for uploading NID card images and displays the extracted information in a structured format.

## Features

-   **Web-based Interface:** A user-friendly interface built with Streamlit for easy image uploads.
-   **OCR Engine:** Utilizes `easyocr` to extract text from NID card images, with support for both English and Bengali languages.
-   **Information Extraction:** Employs regular expressions to parse and extract key information such as name, NID number, date of birth, etc.
-   **Machine Learning Model:** Integrates a YOLO (You Only Look Once) model for object detection to identify the location of the NID card in an image, improving OCR accuracy.

## System Architecture

The project is composed of two main components:

1.  **Frontend:** A Streamlit application (`app/streamlitApp.py`) that provides a user interface for uploading NID card images.
2.  **Backend:** A FastAPI application (`app/app.py`) that handles the OCR process. It receives an image from the frontend, uses a YOLO model to detect the NID card, crops the image, and then uses `easyocr` to extract text from the cropped image.

The frontend and backend communicate via HTTP requests.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd NIDOCR
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Start the backend server:**
    ```bash
    uvicorn app.app:app --reload
    ```
    The backend server will be running at `http://127.0.0.1:8000`.

2.  **Start the frontend application:**
    In a new terminal, run the following command:
    ```bash
    streamlit run app/streamlitApp.py
    ```
    The Streamlit application will open in your browser.

3.  **Upload an NID card image:**
    Use the file uploader in the web interface to select and upload an image of an NID card.

4.  **Extract information:**
    Click the "Extract Info" button to start the OCR process. The extracted information will be displayed in JSON format.

## Training the Model

The YOLO model for NID card detection can be trained using the `OCR/train_yolo.ipynb` notebook. This notebook provides a step-by-step guide to training the model on the provided `synthetic_nid_dataset` or your own dataset.

After training, the best model is saved to `runs/detect/yolo_nid_detection/weights/best.pt`. This is the model that is used by the backend application.

## Project Structure

```
NIDOCR/
├── app/
│   ├── app.py              # FastAPI backend application
│   └── streamlitApp.py     # Streamlit frontend application
├── OCR/
│   ├── bd_nid_ocr.ipynb    # Jupyter notebook for easyocr testing
│   ├── ocr.ipynb           # Jupyter notebook for pytesseract testing
│   └── train_yolo.ipynb    # Jupyter notebook for training the YOLO model
├── runs/
│   └── detect/
│       └── train5/
│           └── weights/
│               └── best.pt # Trained YOLO model
├── synthetic_nid_dataset/  # Dataset for training the YOLO model
│   ├── images/
│   ├── labels/
│   └── ...
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Disclaimer

This project is for educational and demonstration purposes only. The accuracy of the extracted information may vary depending on the quality of the NID card image.