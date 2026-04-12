import os
import sys
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "agent"))

from hindsight_tools import retain, recall, reflect, create_bank
from incident_agent import diagnose_incident, seed_incidents_to_memory, get_patterns

app = FastAPI(title="Incident Response Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class IncidentRequest(BaseModel):
    description: str

class RecallRequest(BaseModel):
    query: str

@app.on_event("startup")
async def startup():
    create_bank()

@app.get("/")
def root():
    return {"status": "ok", "message": "Incident Response Agent is running 🚨"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/seed")
def seed():
    """Seed all past incidents into Hindsight memory."""
    seed_incidents_to_memory()
    return {"status": "success", "message": "Past incidents seeded into memory"}

@app.post("/diagnose")
def diagnose(req: IncidentRequest):
    """Diagnose a new incident using memory + AI."""
    result = diagnose_incident(req.description)
    return {
        "status": "success",
        "incident": req.description,
        "diagnosis": result
    }

@app.post("/recall")
def recall_memories(req: RecallRequest):
    """Search past incident memories."""
    memories = recall(req.query)
    return {
        "status": "success",
        "query": req.query,
        "memories": memories
    }

@app.get("/patterns")
def patterns():
    """Get patterns and insights from all past incidents."""
    result = get_patterns()
    return {
        "status": "success",
        "patterns": result
    }