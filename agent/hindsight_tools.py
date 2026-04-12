import os
import requests
from dotenv import load_dotenv

load_dotenv()

HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "incident-memory")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {HINDSIGHT_API_KEY}"
}

def retain(content: str) -> dict:
    try:
        response = requests.post(
            f"{HINDSIGHT_BASE_URL}/v1/default/banks/{BANK_ID}/memories",
            json={"items": [{"content": content}]},
            headers=HEADERS,
            timeout=60
        )
        if response.status_code in [200, 201, 202]:
            print(f"✅ Retained: {content[:80]}...")
            return response.json()
        print(f"❌ Retain failed: {response.status_code} - {response.text[:200]}")
        return {}
    except Exception as e:
        print(f"❌ Retain failed: {e}")
        return {}

def recall(query: str) -> str:
    try:
        response = requests.post(
            f"{HINDSIGHT_BASE_URL}/v1/default/banks/{BANK_ID}/memories/recall",
            json={"query": query},
            headers=HEADERS,
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if not results:
                return "No relevant past incidents found."
            return "\n\n".join([r.get("text", str(r)) for r in results])
        print(f"❌ Recall failed: {response.status_code} - {response.text[:200]}")
        return "Memory recall unavailable."
    except Exception as e:
        print(f"❌ Recall failed: {e}")
        return "Memory recall unavailable."

def reflect(query: str) -> str:
    try:
        response = requests.post(
            f"{HINDSIGHT_BASE_URL}/v1/default/banks/{BANK_ID}/reflect",
            json={"query": query},
            headers=HEADERS,
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("text", "No reflection available.")
        return "Reflection unavailable."
    except Exception as e:
        print(f"❌ Reflect failed: {e}")
        return "Reflection unavailable."

def create_bank() -> bool:
    try:
        response = requests.put(
            f"{HINDSIGHT_BASE_URL}/v1/default/banks/{BANK_ID}",
            json={"mission": "Remember all past production incidents, root causes, resolutions and patterns to help engineers resolve future incidents faster."},
            headers=HEADERS,
            timeout=30
        )
        print(f"✅ Memory bank '{BANK_ID}' ready")
        return True
    except Exception as e:
        print(f"❌ Bank setup failed: {e}")
        return False