import os
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
from hindsight_tools import retain, recall, reflect, create_bank
from runbooks import get_runbook

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "incident_log.json")


# ─── Utility: load/save local incident log ────────────────────────────────────

def load_log() -> list:
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_log(log: list):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


# ─── Improvement 1: Severity classification ───────────────────────────────────

def classify_severity(description: str) -> str:
    """Classify incident as P1, P2, or P3 using a single fast LLM call."""
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{
                "role": "user",
                "content": (
                    "Classify this incident severity. Reply with ONLY one word: P1, P2, or P3.\n"
                    "P1 = production completely down, data loss, revenue impact.\n"
                    "P2 = major feature broken, significant degradation.\n"
                    "P3 = minor issue, workaround available.\n\n"
                    f"Incident: {description}"
                )
            }],
            max_tokens=5,
            temperature=0
        )
        result = resp.choices[0].message.content.strip().upper()
        if result in ["P1", "P2", "P3"]:
            return result
        return "P2"
    except:
        return "P2"


# ─── Improvement 2: Smart multi-keyword runbook scoring ───────────────────────

KEYWORD_MAP = {
    "database":   ["db", "postgres", "mysql", "sql", "connection", "query", "deadlock", "timeout"],
    "kubernetes": ["k8s", "pod", "kubectl", "deployment", "container", "crashloop", "namespace", "helm"],
    "memory":     ["oom", "memory", "heap", "leak", "ram", "out of memory", "killed"],
    "cpu":        ["cpu", "load", "throttl", "spike", "process", "high utilization", "pegged"],
    "ssl":        ["ssl", "tls", "cert", "https", "certificate", "expired", "handshake"],
    "disk":       ["disk", "storage", "space", "inode", "filesystem", "full", "no space"],
    "network":    ["network", "dns", "timeout", "latency", "firewall", "unreachable", "packet loss"],
    "redis":      ["redis", "cache", "eviction", "maxmemory", "connection refused"],
}

def pick_best_runbook(description: str) -> dict:
    """Score all runbooks against the description and return the best match."""
    desc_lower = description.lower()
    scores = {key: sum(1 for term in terms if term in desc_lower)
              for key, terms in KEYWORD_MAP.items()}
    best_key = max(scores, key=scores.get)
    if scores[best_key] == 0:
        return get_runbook("general")
    return get_runbook(best_key)


# ─── Improvement 3: Auto-reflect every 5 incidents ────────────────────────────

def maybe_auto_reflect(incident_count: int):
    """Trigger a reflect call every 5 incidents and store the insight."""
    if incident_count > 0 and incident_count % 5 == 0:
        print(f"\n🔄 Auto-reflecting on {incident_count} incidents to find patterns...\n")
        insight = reflect(
            "What are the most common recurring patterns across all production incidents? "
            "Which services are most fragile? What should the team prioritize to prevent "
            "future outages? Be specific and actionable."
        )
        if insight and insight != "Reflection unavailable.":
            retain(
                f"[AUTO-REFLECT after {incident_count} incidents — {datetime.now().strftime('%Y-%m-%d')}]: "
                f"{insight}"
            )
            print(f"💡 Pattern insight stored in memory.\n")


# ─── Core: seed past incidents ────────────────────────────────────────────────

def seed_incidents_to_memory():
    """Load all synthetic incidents into Hindsight memory."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_incidents.json")
    with open(data_path, "r") as f:
        incidents = json.load(f)

    print(f"\n🧠 Seeding {len(incidents)} past incidents into memory...\n")
    for inc in incidents:
        memory_text = (
            f"Incident {inc['id']}: {inc['title']}\n"
            f"Severity: {inc['severity']}\n"
            f"Description: {inc['description']}\n"
            f"Root Cause: {inc['root_cause']}\n"
            f"Resolution: {inc['resolution']}\n"
            f"Duration: {inc['duration_minutes']} minutes\n"
            f"Tags: {', '.join(inc['tags'])}"
        )
        retain(memory_text)
    print("\n✅ All incidents loaded into memory!\n")


# ─── Core: diagnose incident (all 4 improvements wired in) ───────────────────

def diagnose_incident(incident_description: str) -> dict:
    """
    Diagnose an incident using memory + LLM.
    Returns a dict with: id, severity, diagnosis
    """

    # Step 1 — Classify severity
    print("\n⚡ Classifying severity...")
    severity = classify_severity(incident_description)
    severity_emoji = {"P1": "🔴", "P2": "🟡", "P3": "🟢"}.get(severity, "🟡")
    print(f"{severity_emoji} Severity: {severity}\n")

    # Step 2 — Recall similar past incidents from Hindsight memory
    print("🔍 Recalling similar past incidents from memory...\n")
    past_incidents = recall(incident_description)

    # Step 3 — Pick best-matching runbook
    runbook = pick_best_runbook(incident_description)

    # Step 4 — Build prompt and call LLM
    system_prompt = (
        "You are an expert Site Reliability Engineer (SRE) with 10+ years of experience. "
        "You help diagnose and resolve production incidents quickly and accurately. "
        "You have access to past incident memory and runbooks. "
        "Be concise, specific, and actionable. Format your response clearly."
    )

    user_prompt = (
        f"## New Incident Report\n"
        f"Severity: {severity}\n"
        f"{incident_description}\n\n"
        f"## Relevant Past Incidents (from Hindsight memory)\n"
        f"{past_incidents}\n\n"
        f"## Suggested Runbook: {runbook['name']}\n"
        f"{chr(10).join(runbook['steps'])}\n\n"
        f"Based on the past incidents and runbook above, provide:\n"
        f"1. **Most Likely Root Cause** — your best diagnosis\n"
        f"2. **Immediate Actions** — top 3 things to do RIGHT NOW\n"
        f"3. **Estimated Resolution Time** — based on similar past incidents\n"
        f"4. **Prevention** — how to stop this happening again\n"
    )

    print("🤖 Analyzing with AI...\n")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=1024
    )
    diagnosis = response.choices[0].message.content

    # Step 5 — Assign incident ID and log locally
    log = load_log()
    inc_id = f"INC{str(len(log) + 11).zfill(3)}"
    log.append({
        "id": inc_id,
        "timestamp": datetime.now().isoformat(),
        "severity": severity,
        "description": incident_description,
        "diagnosis": diagnosis[:500],
        "runbook_used": runbook["name"]
    })
    save_log(log)
    print(f"🗂️  Logged as {inc_id}\n")

    # Step 6 — Retain this incident in Hindsight memory
    print("💾 Storing in Hindsight memory...\n")
    retain(
        f"Incident {inc_id} ({severity}): {incident_description}\n"
        f"Runbook used: {runbook['name']}\n"
        f"Diagnosis: {diagnosis[:300]}"
    )

    # Step 7 — Auto-reflect every 5 incidents
    maybe_auto_reflect(len(log))

    return {
        "id": inc_id,
        "severity": severity,
        "diagnosis": diagnosis
    }


# ─── Core: get patterns via reflect ──────────────────────────────────────────

def get_patterns() -> str:
    """Use Hindsight reflect to synthesize patterns across all incidents."""
    print("\n🧠 Reflecting on all past incidents to find patterns...\n")
    return reflect(
        "What are the most common patterns and recurring issues across all production incidents? "
        "Which services or components fail most often? "
        "What should the team prioritize to prevent future incidents?"
    )


# ─── CLI interface ────────────────────────────────────────────────────────────

def run_cli():
    print("=" * 60)
    print("🚨 INCIDENT RESPONSE AGENT — Powered by Hindsight Memory")
    print("=" * 60)

    create_bank()

    while True:
        print("\nWhat would you like to do?")
        print("1. Seed past incidents into memory")
        print("2. Diagnose a new incident")
        print("3. Get patterns from past incidents")
        print("4. View incident history")
        print("5. Exit")
        print("-" * 40)
        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            seed_incidents_to_memory()

        elif choice == "2":
            print("\nDescribe the incident (press Enter twice when done):")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            incident = " ".join(lines)
            if incident:
                result = diagnose_incident(incident)
                print("\n" + "=" * 60)
                print(f"📋 DIAGNOSIS REPORT — {result['id']} [{result['severity']}]")
                print("=" * 60)
                print(result["diagnosis"])
            else:
                print("⚠️  No incident description provided.")

        elif choice == "3":
            patterns = get_patterns()
            print("\n" + "=" * 60)
            print("📊 INCIDENT PATTERNS & INSIGHTS")
            print("=" * 60)
            print(patterns)

        elif choice == "4":
            log = load_log()
            if not log:
                print("\n⚠️  No incidents logged yet. Run option 2 first.")
            else:
                print(f"\n📜 Incident History ({len(log)} total)\n")
                print(f"{'ID':<8} {'Severity':<10} {'Timestamp':<22} {'Description'}")
                print("-" * 70)
                for inc in reversed(log[-10:]):
                    ts = inc["timestamp"][:16].replace("T", " ")
                    desc = inc["description"][:40] + "..."
                    emoji = {"P1": "🔴", "P2": "🟡", "P3": "🟢"}.get(inc["severity"], "⚪")
                    print(f"{inc['id']:<8} {emoji} {inc['severity']:<8} {ts:<22} {desc}")

        elif choice == "5":
            print("\n👋 Goodbye!")
            break

        else:
            print("⚠️  Invalid choice. Enter 1-5.")


if __name__ == "__main__":
    run_cli()