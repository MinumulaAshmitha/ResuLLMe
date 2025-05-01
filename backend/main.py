from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
import json
from datetime import datetime
import logging
from pythonjsonlogger import jsonlogger
import os
import tempfile

from ollama_client import OllamaClient
from docx_generator import DocxGenerator
from resume_parser import ResumeParser

# Configure logging
logger = logging.getLogger(__name__)
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI(title="ResuLLMe API")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
ollama_client = OllamaClient()
docx_generator = DocxGenerator()
resume_parser = ResumeParser()

# In-memory storage for sessions and user data
sessions: Dict[str, Dict] = {}
resume_data: Dict[str, Dict] = {}

# Conversation flow
CONVERSATION_FLOW = [
    {"question": "What is your full name?", "field": "name"},
    {"question": "What is your title/domain (e.g., Software Engineer)?", "field": "title"},
    {"question": "What is your phone number?", "field": "phone"},
    {"question": "What is your email address?", "field": "email"},
    {"question": "What is your current location?", "field": "location"},
    {"question": "Give a brief personal description (this will be expanded by Ollama into a full profile summary).", "field": "summary"},
    {"question": "Which college/university did you attend?", "field": "education"},
    {"question": "What is your degree and major?", "field": "education_degree"},
    {"question": "What is your current year of study or passing year?", "field": "education_year"},
    {"question": "What is your CGPA or percentage?", "field": "education_cgpa"},
    {"question": "What are your skills (comma-separated)?", "field": "skills"},
    {"question": "Provide your projects (title and description).", "field": "projects"},
    {"question": "Describe your work experience (job title, company, duration, and description).", "field": "experience"},
    {"question": "List any certifications (name, issuer, and date).", "field": "certifications"}
]

class SessionRequest(BaseModel):
    user_id: Optional[str] = None

    class Config:
        extra = "allow"  # Allow extra fields in the request

class ChatMessage(BaseModel):
    session_id: str
    message: str

class ResumeData(BaseModel):
    name: str
    title: str
    phone: str
    email: str
    location: str
    summary: str
    education: List[Dict]
    skills: List[str]
    projects: List[Dict]
    experience: List[Dict]
    certifications: List[Dict]

@app.post("/api/session")
async def start_session(request: SessionRequest = None):
    if request is None:
        request = SessionRequest()
        
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "created_at": datetime.now().isoformat(),
        "user_id": request.user_id,
        "messages": [],
        "current_step": 0,
        "resume_data": {}
    }
    logger.info(f"New session started: {session_id}")
    return {
        "session_id": session_id,
        "question": CONVERSATION_FLOW[0]["question"]
    }

@app.post("/api/chat")
async def chat(message: ChatMessage):
    if message.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[message.session_id]
    current_step = session["current_step"]
    
    # Store the message
    session["messages"].append({
        "text": message.message,
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        # Check if this is a resume generation request
        if "generate" in message.message.lower() and "resume" in message.message.lower():
            if current_step < len(CONVERSATION_FLOW):
                return {
                    "response": "Please complete all the questions first before generating your resume.",
                    "question": CONVERSATION_FLOW[current_step]["question"]
                }
            
            # Ensure all required fields are present in the resume data
            for field in ['name', 'title', 'phone', 'email', 'location', 'summary', 
                         'education', 'skills', 'projects', 'experience', 'certifications']:
                if field not in session["resume_data"]:
                    session["resume_data"][field] = ""
            
            # Log the original resume data
            logger.info(f"Original resume data: {json.dumps(session['resume_data'], indent=2)}")
            
            # Enhance the resume data using Ollama
            enhanced_data = await ollama_client.enhance_resume(session["resume_data"])
            
            # Log the enhanced resume data
            logger.info(f"Enhanced resume data: {json.dumps(enhanced_data, indent=2)}")
            
            # Store the enhanced resume data
            resume_data[message.session_id] = enhanced_data
            
            return {
                "response": "I've generated your resume! I've enhanced it with additional details to make it more professional. You can preview it below and download it as a DOCX file.",
                "resume_data": enhanced_data,
                "completed": True
            }
        
        # Process current step
        current_field = CONVERSATION_FLOW[current_step]["field"]
        
        # Parse the response based on the field type
        if current_field == "skills":
            session["resume_data"][current_field] = [skill.strip() for skill in message.message.split(",")]
        elif current_field == "education":
            # Initialize education array if it doesn't exist
            if "education" not in session["resume_data"]:
                session["resume_data"]["education"] = []
            # Add new education entry
            session["resume_data"]["education"].append({
                "institution": message.message,
                "degree": "",
                "year_range": "",
                "cgpa": "",
                "location": ""
            })
        elif current_field == "education_degree":
            # Update the most recent education entry
            if session["resume_data"]["education"]:
                session["resume_data"]["education"][-1]["degree"] = message.message
        elif current_field == "education_year":
            # Update the most recent education entry
            if session["resume_data"]["education"]:
                session["resume_data"]["education"][-1]["year_range"] = message.message
        elif current_field == "education_cgpa":
            # Update the most recent education entry
            if session["resume_data"]["education"]:
                session["resume_data"]["education"][-1]["cgpa"] = message.message
        elif current_field == "projects":
            session["resume_data"][current_field] = [{
                "name": message.message.split(":")[0].strip(),
                "description": message.message.split(":")[1].strip() if ":" in message.message else ""
            }]
        elif current_field == "experience":
            session["resume_data"][current_field] = [{
                "title": message.message.split(",")[0].strip(),
                "company": message.message.split(",")[1].strip() if "," in message.message else "",
                "duration": message.message.split(",")[2].strip() if len(message.message.split(",")) > 2 else "",
                "description": message.message.split(",")[3].strip() if len(message.message.split(",")) > 3 else ""
            }]
        elif current_field == "certifications":
            session["resume_data"][current_field] = [{
                "title": message.message.split(",")[0].strip(),
                "issuer": message.message.split(",")[1].strip() if "," in message.message else "",
                "date": message.message.split(",")[2].strip() if len(message.message.split(",")) > 2 else ""
            }]
        else:
            session["resume_data"][current_field] = message.message
        
        # Move to next step
        session["current_step"] += 1
        
        if session["current_step"] < len(CONVERSATION_FLOW):
            return {
                "response": "Got it!",
                "question": CONVERSATION_FLOW[session["current_step"]]["question"]
            }
        else:
            # Ensure all required fields are present in the resume data
            for field in ['name', 'title', 'phone', 'email', 'location', 'summary', 
                         'education', 'skills', 'projects', 'experience', 'certifications']:
                if field not in session["resume_data"]:
                    session["resume_data"][field] = ""
            
            # Log the original resume data
            logger.info(f"Original resume data: {json.dumps(session['resume_data'], indent=2)}")
            
            # Enhance the resume data using Ollama when all questions are answered
            enhanced_data = await ollama_client.enhance_resume(session["resume_data"])
            
            # Log the enhanced resume data
            logger.info(f"Enhanced resume data: {json.dumps(enhanced_data, indent=2)}")
            
            resume_data[message.session_id] = enhanced_data
            
            return {
                "response": "Thank you! I've enhanced your resume with additional details. Type 'Generate my resume' to proceed.",
                "resume_data": enhanced_data,
                "completed": True
            }
            
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing message")

@app.post("/api/generate")
async def generate_resume(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Generate resume using Ollama
        markdown_resume = await ollama_client.generate_resume(sessions[session_id])
        
        # Parse markdown to JSON
        parsed_resume = resume_parser.parse_markdown_to_json(markdown_resume)
        
        # Store the resume data
        resume_data[session_id] = parsed_resume
        
        return parsed_resume
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating resume")

@app.get("/api/resume_preview/{session_id}")
async def get_resume_preview(session_id: str):
    if session_id not in resume_data:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return templates.TemplateResponse(
        "resume.html",
        {
            "request": None,  # Required by FastAPI
            "resume": resume_data[session_id],
            "session_id": session_id
        }
    )

@app.get("/api/download/{session_id}")
async def download_resume(session_id: str):
    if session_id not in resume_data:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            output_path = temp_file.name
        
        # Generate the DOCX file
        docx_generator.generate_resume(resume_data[session_id], output_path)
        
        # Return the file
        return FileResponse(
            output_path,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=f"resume_{session_id}.docx"
        )
    except Exception as e:
        logger.error(f"Error generating DOCX: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating DOCX")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 