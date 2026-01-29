import fitz  # PyMuPDF

def extract_lab_values(uploaded_file):
    """
    Extracts raw text from the uploaded PDF file.
    This serves as the 'Structured Parsing' layer.
    """
    if uploaded_file is None:
        return {"raw_text": ""}
    
    try:
        # פתיחת הקובץ מהזיכרון
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        # איסוף הטקסט מכל העמודים
        for page in doc:
            text += page.get_text()
        return {"raw_text": text}
    except Exception as e:
        return {"raw_text": f"Error reading PDF: {str(e)}"}