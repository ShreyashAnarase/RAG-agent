import fitz

async def extract_text_from_pdf(file) -> str:
    file_bytes = await file.read()
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf_doc: 
        text = "".join(page.get_text() for page in pdf_doc)
        return text.strip()

