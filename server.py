from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import re

app = FastAPI(title="Holehe API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok", "service": "holehe-api"}

@app.get("/check")
def check(email: str = Query(..., description="Email to scan")):
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return {"error": "invalid email"}

    try:
        r = subprocess.run(
            ["holehe", email, "--only-used", "--no-color"],
            capture_output=True,
            text=True,
            timeout=90,
        )

        found = []
        for line in r.stdout.splitlines():
            m = re.search(r"\[\+\]\s+Email used on\s+(.+)", line, re.IGNORECASE)
            if m:
                found.append({
                    "name": m.group(1).strip(),
                    "details": "account found"
                })

        return {
            "email": email,
            "checked": 120,
            "found": found,
        }

    except subprocess.TimeoutExpired:
        return {"email": email, "checked": 0, "found": [], "error": "timeout"}
    except Exception as e:
        return {"email": email, "checked": 0, "found": [], "error": str(e)}
