import os
import json
from groq import Groq
from dotenv import load_dotenv
from hindsight_tools import retain, recall, reflect, create_bank
from runbooks import get_runbook

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def seed_incidents_to_memory():
    """Load all synthetic incidents into Hindsight memory."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_incidents.json")
    with open(data_path, "r") as f:
        incidents = json.load(f)

    print(f"\n🧠 Seeding {len(incidents)} past incidents into memory...\n")
    for inc in incidents:
        memory_text = f"""
Incident {inc['id']}: {inc['title']}
Severity: {inc['severity']}
Description: {inc['description']}
Root Cause: {inc['root_cause']}
Resolution: {inc['resolution']}
Duration: {inc['duration_minutes']} minutes
Tags: {', '.join(inc['tags'])}
        """.strip()
        retain(memory_text)
    print("\n✅ All incidents loaded into memory!\n")

def diagnose_incident(incident_description: str) -> str:
    """Main agent function - diagnose an incident using memory + LLM."""

    print(f"\n🔍 Recalling similar past incidents...\n")
    past_incidents = recall(incident_description)

    runbook_key = "general"
    keywords = ["database", "postgres", "kubernetes", "memory", "cpu", "ssl", "disk", "network", "redis", "docker"]
    for kw in keywords:
        if kw in incident_description.lower():
            runbook_key = kw
            break
    runbook = get_runbook(runbook_key)

    system_prompt = """You are an expert Site Reliability Engineer (SRE) with 10+ years of experience.
You help diagnose and resolve production incidents quickly and accurately.
You have access to past incident memory and runbooks.
Be concise, specific, and actionable. Format your response clearly."""

    user_prompt = f"""
## New Incident Report
{incident_description}

## Relevant Past Incidents (from memory)
{past_incidents}

## Suggested Runbook: {runbook['name']}
{chr(10).join(runbook['steps'])}

Based on the past incidents and runbook above, provide:
1. **Most Likely Root Cause** - your best diagnosis
2. **Immediate Actions** - top 3 things to do RIGHT NOW
3. **Estimated Resolution Time** - based on similar past incidents
4. **Prevention** - how to stop this happening again
"""

    print(f"🤖 Analyzing incident with AI...\n")
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

    print(f"💾 Storing this incident in memory...\n")
    retain(f"New incident reported: {incident_description}\nDiagnosis provided: {diagnosis[:300]}")

    return diagnosis

def get_patterns() -> str:
    """Use reflect to find patterns across all incidents."""
    print("\n🧠 Reflecting on all past incidents to find patterns...\n")
    return reflect("What are the most common patterns and recurring issues across all production incidents? What should the team focus on to prevent future incidents?")

def run_cli():
    """Simple CLI to interact with the agent."""
    print("=" * 60)
    print("🚨 INCIDENT RESPONSE AGENT - Powered by Hindsight Memory")
    print("=" * 60)

    create_bank()

    print("\nWhat would you like to do?")
    print("1. Seed past incidents into memory")
    print("2. Diagnose a new incident")
    print("3. Get patterns from past incidents")
    print("4. Exit")

    while True:
        print("\n" + "-" * 40)
        choice = input("Enter choice (1-4): ").strip()

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
                print("📋 DIAGNOSIS REPORT")
                print("=" * 60)
                print(result)
            else:
                print("⚠️  No incident description provided.")

        elif choice == "3":
            patterns = get_patterns()
            print("\n" + "=" * 60)
            print("📊 INCIDENT PATTERNS & INSIGHTS")
            print("=" * 60)
            print(patterns)

        elif choice == "4":
            print("\n👋 Goodbye!")
            break

        else:
            print("⚠️  Invalid choice. Enter 1, 2, 3 or 4.")

if __name__ == "__main__":
    run_cli()