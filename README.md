<div align="center">

```
██╗███╗   ██╗ ██████╗██╗██████╗ ███████╗███╗   ██╗████████╗
██║████╗  ██║██╔════╝██║██╔══██╗██╔════╝████╗  ██║╚══██╔══╝
██║██╔██╗ ██║██║     ██║██║  ██║█████╗  ██╔██╗ ██║   ██║   
██║██║╚██╗██║██║     ██║██║  ██║██╔══╝  ██║╚██╗██║   ██║   
██║██║ ╚████║╚██████╗██║██████╔╝███████╗██║ ╚████║   ██║   
╚═╝╚═╝  ╚═══╝ ╚═════╝╚═╝╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝  
    R E S P O N S E   A G E N T   —   P O W E R E D   B Y   H I N D S I G H T
```

<br/>

**An AI-powered DevOps agent that remembers every incident, learns from every resolution, and gets smarter with every outage.**

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-LLM-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![Hindsight](https://img.shields.io/badge/Hindsight-Memory-6C3DE0?style=for-the-badge)](https://hindsight.vectorize.io)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

<br/>

> 🏆 Built for the **Hindsight Hackathon** — HackWithChennai 2026  
> 🧠 Uses **retain · recall · reflect** to build a living memory of your infrastructure

<br/>

---

</div>

## 🚨 The Problem

Every DevOps team faces the same nightmare:

- Production goes down at 2 AM
- The engineer on-call has never seen this error before
- They spend 45 minutes digging through Slack history, Confluence docs, and old Jira tickets
- They finally find that *someone fixed this exact issue 3 months ago*
- Total downtime: **2 hours**. Total cost: **thousands of dollars**.

**The root cause isn't the bug. It's organizational amnesia.**

---

## 💡 The Solution

The **Incident Response Agent** is an AI SRE that never forgets. Every time an incident occurs, it:

1. **Remembers** — stores the incident, root cause, and resolution in persistent memory
2. **Recalls** — when a new incident strikes, it instantly surfaces similar past incidents
3. **Reflects** — synthesizes patterns across all incidents to proactively prevent future outages

It's not a chatbot. It's a **living ops brain** that compounds knowledge over time.

---

## ✨ Demo: Before vs After

### ❌ Without Memory (Generic LLM)
```
User: Our Kubernetes pods are in CrashLoopBackOff after a config update.

LLM: CrashLoopBackOff usually means the container is crashing repeatedly.
     Check your logs with kubectl logs <pod-name>. Common causes include
     misconfiguration, missing dependencies, or resource limits...
```
*Generic. Unhelpful. You already knew this.*

### ✅ With Hindsight Memory (Our Agent)
```
User: Our Kubernetes pods are in CrashLoopBackOff after a config update.

Agent: 🔍 Recalling similar past incidents...

       MATCH FOUND — INC004 (18 min resolution):
       "Payment service pods entered CrashLoopBackOff after config map 
        update. Root cause: missing PAYMENT_API_KEY environment variable."

       📋 DIAGNOSIS:
       Most Likely Cause: Missing env var in config map after your update.
       
       Immediate Actions:
       1. kubectl get configmap -o yaml → check PAYMENT_API_KEY is present
       2. kubectl describe pod <pod-name> → look for "env var not found"  
       3. kubectl rollout restart deployment/payment-service after fix
       
       Estimated Resolution: ~18 minutes (based on past incident)
       Prevention: Add config validation step to your CI/CD pipeline
```
*Specific. Actionable. Based on real institutional memory.*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER / ENGINEER                          │
└─────────────────────────┬───────────────────────────────────┘
                          │ describes incident
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND                            │
│              api/main.py  :8000                             │
└──────┬──────────────────┬──────────────────┬───────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────┐  ┌───────────────┐  ┌──────────────────────┐
│  RUNBOOKS    │  │ GROQ LLM API  │  │  HINDSIGHT MEMORY    │
│ runbooks.py  │  │llama-3.3-70b  │  │   vectorize.io       │
│              │  │               │  │                      │
│ • database   │  │  Diagnosis    │  │  retain()  ←─ store  │
│ • kubernetes │  │  Generation   │  │  recall()  ←─ search │
│ • memory     │  │               │  │  reflect() ←─ learn  │
│ • cpu/disk   │  └───────────────┘  └──────────────────────┘
│ • ssl/network│
└──────────────┘
```

---

## 🧠 How Hindsight Memory Works

Hindsight provides three core memory operations that power this agent:

| Operation | What it does | When we use it |
|-----------|-------------|----------------|
| `retain()` | Stores incident details as persistent memory | After every incident is reported or resolved |
| `recall()` | Semantically searches past incidents by similarity | Before diagnosing any new incident |
| `reflect()` | Synthesizes patterns across all stored memories | Weekly ops reviews, proactive prevention |

### Memory Flow

```
New Incident Reported
        │
        ▼
   recall(incident)  ──→  Top 5 similar past incidents
        │
        ▼
   LLM Diagnosis  ──→  Root cause + actions + timeline
        │
        ▼
   retain(result)  ──→  Stored for future recall
        │
        ▼
   (Weekly) reflect()  ──→  "Database issues spike on Fridays after deploy"
```

---

## 📁 Project Structure

```
incident-response-agent/
│
├── 📁 agent/
│   ├── incident_agent.py      # Main agent loop — CLI interface
│   ├── hindsight_tools.py     # retain / recall / reflect wrappers
│   └── runbooks.py            # 8 domain-specific runbooks
│
├── 📁 api/
│   └── main.py                # FastAPI REST API (5 endpoints)
│
├── 📁 data/
│   └── synthetic_incidents.json   # 10 realistic past incidents
│
├── 📁 frontend/               # Dashboard (coming soon)
│
├── .env                       # API keys (not committed)
├── requirements.txt           # Python dependencies
└── README.md                  # You are here
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Groq API Key](https://console.groq.com) (free)
- [Hindsight Cloud Account](https://ui.hindsight.vectorize.io) (free)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/incident-response-agent.git
cd incident-response-agent
```

### 2. Set up virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn hindsight-client groq python-dotenv requests
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_BANK_ID=incident-memory
HINDSIGHT_API_KEY=your_hindsight_cloud_key_here
```

### 5. Run the agent

```bash
cd agent
python incident_agent.py
```

### 6. Seed past incidents into memory

```
Enter choice (1-4): 1
```

This loads 10 realistic past incidents into Hindsight memory — giving the agent its initial knowledge base.

### 7. Diagnose your first incident

```
Enter choice (1-4): 2
```

Describe any production incident and watch the agent recall relevant past incidents and generate a targeted diagnosis.

---

## 🌐 REST API

Start the API server:

```bash
cd api
uvicorn main:app --reload --port 8000
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | GET | Health check |
| `POST /seed` | POST | Load all past incidents into memory |
| `POST /diagnose` | POST | Diagnose a new incident |
| `POST /recall` | POST | Search past incident memories |
| `GET /patterns` | GET | Get patterns via reflect() |

### Example API call

```bash
curl -X POST http://localhost:8000/diagnose \
  -H "Content-Type: application/json" \
  -d '{"description": "Kubernetes pods in CrashLoopBackOff after config update"}'
```

---

## 📊 Judging Criteria Coverage

| Criteria | Weight | How We Address It |
|----------|--------|-------------------|
| **Innovation** | 30% | AI agent with persistent memory that compounds knowledge — not a stateless chatbot |
| **Use of Hindsight Memory** | 25% | All 3 operations used: `retain`, `recall`, `reflect` with clear before/after contrast |
| **Technical Implementation** | 20% | Python agent + FastAPI backend + Hindsight Cloud + Groq LLM |
| **User Experience** | 15% | CLI with clear menus, emoji feedback, structured diagnosis reports |
| **Real-world Impact** | 10% | Every engineering team loses hours to repeated incidents — this solves that |

---

## 🗺️ Roadmap

- [ ] React dashboard with incident timeline visualization
- [ ] Slack/PagerDuty webhook integration for auto-triggered diagnosis
- [ ] Auto-reflect weekly report generation
- [ ] Multi-team memory banks (per service/squad)
- [ ] Severity prediction based on memory patterns

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Memory | [Hindsight by Vectorize](https://hindsight.vectorize.io) |
| LLM | [Groq](https://groq.com) — llama-3.3-70b-versatile |
| Backend | [FastAPI](https://fastapi.tiangolo.com) |
| Agent | Python 3.10+ |
| HTTP Client | requests |

---

## 👥 Team

Built with ❤️ by **Team [Your Team Name]** for the **Hindsight Hackathon — HackWithChennai 2026**

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**If your production system has ever gone down for the same reason twice — this agent is for you.**

⭐ Star this repo if you found it useful!

</div>
