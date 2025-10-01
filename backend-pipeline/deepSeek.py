"""
deepSeek.py

Pipeline:
  1. Read resume PDF using pdfminer.six
  2. Build a strict prompt requesting ONLY JSON with a fixed schema
  3. Call OpenRouter chat completions endpoint
  4. Try to parse JSON; if parsing fails, call a small JSON-fixer prompt once
  5. Return validated JSON
"""

import json, re, os, requests, yaml
from pdfminer.high_level import extract_text
from typing import Any, Dict

# -------------------------
# Config
# -------------------------
BASE_DIR = os.path.dirname(__file__)  
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")  

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"Could not find config.yaml at {CONFIG_PATH}")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

OPENROUTER_API_KEY = cfg.get("OPENROUTER_API_KEY", "")
MODEL = cfg.get("MODEL", "deepseek/deepseek-chat-v3.1:free")
MAX_TOKENS = int(cfg.get("MAX_TOKENS", 2000))

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_API_KEY:
    raise SystemExit("Please set OPENROUTER_API_KEY in config.yaml")

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Resume Parser",
    "Content-Type": "application/json",
}

# -------------------------
# Helpers
# -------------------------
def read_pdf(path: str) -> str:
    """Extract text from a text-based PDF."""
    try:
        text = extract_text(path)
        text = re.sub(r"\s+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"PDF extraction failed: {e}")

SCHEMA = {
    "full_name": "string",
    "title": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "summary": "string",
    "linkedin": "string",
    "portfolio": [{"platform": "string", "url": "string"}],
    "education": [
        {"degree": "string", "institution": "string", "start_year": "string", "end_year": "string", "description": "string"}
    ],
    "experience": [
        {"company": "string", "title": "string", "start_year": "string", "end_year": "string", "description": ["string"]}
    ],
    "projects": [
        {"project_name": "string", "start_year": "string", "end_year": "string", "description": ["string"]}
    ],
    "technical_skills": ["string"],
    "certifications": ["string"],
    "languages": ["string"]
}

SYSTEM_INSTRUCTION = (
    "You are a professional resume parser. Extract fields ONLY into valid JSON. "
    "Empty string/list if not present. Do NOT hallucinate or add explanations."
)

def build_user_prompt(resume_text: str) -> str:
    schema_json = json.dumps(SCHEMA, indent=2)
    return f"""
Parse the following resume text into VALID JSON:

Schema:
{schema_json}

Resume text:
\"\"\"{resume_text}\"\"\"

Constraints:
- Return only one valid JSON object, nothing else.
- Use empty strings/lists when fields not found.
- Use YYYY for years if possible.
"""

# -------------------------
# OpenRouter API call
# -------------------------
def call_openrouter_chat(messages: list, model: str = MODEL, max_tokens: int = MAX_TOKENS, temperature: float = 0.0):
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    r = requests.post(OPENROUTER_CHAT_URL, json=payload, headers=HEADERS, timeout=120)
    
    print("DEBUG STATUS:", r.status_code)
    print("DEBUG RESPONSE (first 200 chars):", r.text[:200])
    
    r.raise_for_status()
    return r.json()

def extract_json_from_text(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        pass
    first, last = text.find("{"), text.rfind("}")
    if first != -1 and last != -1 and last > first:
        try:
            return json.loads(text[first:last+1])
        except Exception:
            return None
    return None

def fix_json_with_model(prev_raw: str) -> Any:
    fix_system = "You are a JSON fixer. Convert the following text into valid JSON only."
    messages = [
        {"role": "system", "content": fix_system},
        {"role": "user", "content": prev_raw}
    ]
    resp = call_openrouter_chat(messages)
    content = resp["choices"][0]["message"]["content"]
    return extract_json_from_text(content), content

# -------------------------
# Main pipeline
# -------------------------
def parse_resume_with_openrouter(pdf_path: str, retry_fix: bool = True) -> Dict[str, Any]:
    text = read_pdf(pdf_path)
    if not text:
        raise ValueError("No text extracted from PDF. Use OCR if scanned.")

    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": build_user_prompt(text)},
    ]

    print("-> Sending resume to model...")
    resp = call_openrouter_chat(messages)
    model_content = resp["choices"][0]["message"]["content"]

    parsed = extract_json_from_text(model_content)
    if parsed:
        return parsed

    if retry_fix:
        print("Invalid JSON. Retrying with fixer...")
        fixed, raw = fix_json_with_model(model_content)
        return fixed or {"error": "Could not fix JSON", "raw_output": raw}

    return {"error": "Could not parse model output", "raw_output": model_content}


# -------------------------
# CLI Testing
# -------------------------
if __name__ == "__main__":
    test_pdf = r"D:\Work\DevGate\CV Parser+Converter\test resume.pdf"
    if os.path.exists(test_pdf):
        result = parse_resume_with_openrouter(test_pdf, retry_fix=True)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(" No test resume found.")
