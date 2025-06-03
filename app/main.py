from ensurepip import bootstrap
from fastapi import FastAPI, Request, Form
from contextlib import asynccontextmanager
import multiprocessing
from fastapi.templating import Jinja2Templates
import Lchain
from enum import Enum
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
import os
from fastapi import UploadFile, File 
from kafka import KafkaProducer
import json
from kafka_producer import send_to_kafka
import multiprocessing
from pdf_extractor import extract_text_from_pdf

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")


# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting...")

    yield  # This is where FastAPI runs

    # Cleanup resources on shutdown
    print("Shutting down... Cleaning up resources.")
    for process in multiprocessing.active_children():
        process.terminate()
        process.join()
 
app = FastAPI(lifespan=lifespan)
# Serve static files from "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")
# jinja templates for dynamic HTML 
templates = Jinja2Templates(directory="templates")
default_route = ["get_info","get_routes","get_model","openapi", "swagger_ui_redirect"]


class UserMessage(BaseModel):
    message: str

context = None
first_msg = True

# Serve Home page
@app.get("/", response_class=HTMLResponse)
async def serve_home():
   return FileResponse("templates/chatbox.html")


#Uploads documents to the kafka topic 
@app.post("/upload-doc/")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename
    content_type = file.content_type
    doc_id = filename
    try:
        if filename.endswith(".pdf") or content_type == "application/pdf":
            content = await(extract_text_from_pdf(file)) 
            print( f"PDF document '{doc_id}' uploaded and sent for processing.")
        else:
            content = (await file.read()).decode('utf-8')
            
        send_to_kafka("documents-uploaded", {"doc_id": doc_id, "content": content})
        
        return {"message": f"Document '{doc_id}' received and queued for chunking"}
    except:
        print(" Error Uploading file ")
        return {"message": f"Error uploading Document '{doc_id}' "}




# V2 repsond with context 
@app.post("/chat")
async def get_context_based_resonse(user_message: UserMessage):
    global first_msg
    global context
    msg = user_message.message
    # should query for context only on first msg 
    if first_msg:
        context = await get_context(msg)
        first_msg = False

    resp = await bot_response(msg,context)
    print( f"bot_reply: {resp}") 
    # return in correct format 
    resp = jsonable_encoder(resp)
    return JSONResponse(content=resp)


async def bot_response(input_msg,context=None):
    if not context:
        resp = Lchain.get_response(input_msg)
    else:
        resp = Lchain.get_context_based_resp(input_msg,context=context)
    print(resp)
    return {resp}

async def get_context(input_msg):
    context = Lchain.get_context_from_DB(input_msg)
    return context



