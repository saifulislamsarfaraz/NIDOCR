# filename: frontend.py
import streamlit as st
import requests

st.title("NID Card OCR Info Extractor")

uploaded_file = st.file_uploader("Upload NID image", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, caption='Uploaded Image')
    if st.button("Extract Info"):
        with st.spinner("Processing..."):
            response = requests.post(
                "http://127.0.0.1:8000/extract-nid",
                files={"file": uploaded_file.getvalue()}
            )
            if response.ok:
                data = response.json()
                st.success("Extraction Complete!")
                st.json(data)
            else:
                st.error("Failed to extract data.")
