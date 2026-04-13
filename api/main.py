import os
import sys
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "agent"))

from hindsight_tools import retain, recall, reflect, create_bank
from incident_agent import diagnose_incident, seed_incidents_to_memory, get_patterns, load_log

app = FastAPI(title="Incident Response Agent API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request models ───────────────────────────────────────────────────────────

class IncidentRequest(BaseModel):
    description: str

class RecallRequest(BaseModel):
    query: str


# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    create_bank()


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Incident Response Agent is running 🚨",
        "version": "2.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}


# ─── Seed ─────────────────────────────────────────────────────────────────────

@app.post("/seed")
def seed():
    """Load all past incidents into Hindsight memory."""
    try:
        seed_incidents_to_memory()
        return {"status": "success", "message": "Past incidents seeded into memory"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Diagnose ─────────────────────────────────────────────────────────────────

@app.post("/diagnose")
def diagnose(req: IncidentRequest):
    """
    Diagnose a new incident using memory + AI.
    Returns: id, severity, diagnosis
    """
    if not req.description.strip():
        raise HTTPException(status_code=400, detail="Incident description cannot be empty.")
    try:
        result = diagnose_incident(req.description)
        return {
            "status": "success",
            "id": result["id"],
            "severity": result["severity"],
            "incident": req.description,
            "diagnosis": result["diagnosis"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Recall ───────────────────────────────────────────────────────────────────

@app.post("/recall")
def recall_memories(req: RecallRequest):
    """Search past incident memories from Hindsight."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        memories = recall(req.query)
        return {
            "status": "success",
            "query": req.query,
            "memories": memories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Patterns ─────────────────────────────────────────────────────────────────

@app.get("/patterns")
def patterns():
    """Get recurring patterns and insights from all past incidents."""
    try:
        result = get_patterns()
        return {"status": "success", "patterns": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── History (NEW) ────────────────────────────────────────────────────────────

@app.get("/history")
def history():
    """
    Return all locally logged incidents from incident_log.json.
    Used by the frontend to show the incident history panel.
    """
    try:
        log = load_log()
        return {
            "status": "success",
            "total": len(log),
            "incidents": list(reversed(log))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Stats (NEW) ──────────────────────────────────────────────────────────────

@app.get("/stats")
def stats():
    """
    Return summary stats for the dashboard header.
    Total incidents, breakdown by severity.
    """
    try:
        log = load_log()
        p1 = sum(1 for i in log if i.get("severity") == "P1")
        p2 = sum(1 for i in log if i.get("severity") == "P2")
        p3 = sum(1 for i in log if i.get("severity") == "P3")
        return {
            "status": "success",
            "total": len(log),
            "p1": p1,
            "p2": p2,
            "p3": p3
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))