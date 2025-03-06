from fastapi import FastAPI,File,UploadFile,HTTPException
from typing import Annotated
import os
from fastapi.responses import FileResponse
import uuid
import pdfplumber

app = FastAPI()

UPLOAD_FOLDER = "uploaded_file"
os.makedirs(UPLOAD_FOLDER,exist_ok=True)

def generate_new_filename(original_filename: str) -> str:
    extension = original_filename.split(".")[-1]
    new_filename = f"{uuid.uuid4()}.{extension}"
    return new_filename

def extract_text_from_pdf(pdf_file_path: str) -> str:
    with pdfplumber.open(pdf_file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

@app.post('/fileupload')
async def upload_file(file:UploadFile = File(...)) :
    new_filename = generate_new_filename(file.filename)
    file_location = os.path.join(UPLOAD_FOLDER, new_filename)
    with open(file_location, "wb") as f:
            f.write(await file.read())

    ex_content = ""
    if file.filename.lower().endswith('.pdf'):
        ex_content = extract_text_from_pdf(file_location)
    elif file.filename.lower().endswith('.txt'):
        with open(file_location,'r') as f:
            ex_content = f.read()
    return {"message" : "uploaded..","file name" : new_filename,"content type" : file.content_type,"content" : ex_content}
    
@app.get('/download/{file_name}')
def download_file(file_name: str):
    file_location = os.path.join(UPLOAD_FOLDER, file_name)  
    if os.path.exists(file_location):  
        return FileResponse(file_location)
    else:
        raise HTTPException(status_code=404, detail="File not found")
