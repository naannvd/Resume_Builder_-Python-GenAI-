"""
deepseek_openrouter_parser.py

Pipeline:
  1. Read resume PDF using pdfminer.six
  2. Build a strict prompt requesting ONLY JSON with a fixed schema
  3. Call OpenRouter chat completions endpoint
  4. Try to parse JSON; if parsing fails, call a small JSON-fixer prompt once
  5. Return/print validated JSON
"""

import json
import re
import yaml
import requests
from pdfminer.high_level import extract_text
from typing import Any, Dict

# -------------------------
# Config
# -------------------------
CONFIG_PATH = "config.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

OPENROUTER_API_KEY = cfg.get("OPENROUTER_API_KEY") or cfg.get("OPENROUTER_KEY") or ""
MODEL = "deepseek/deepseek-chat-v3.1:free"
MODEL = cfg.get("MODEL", MODEL)
MAX_TOKENS = int(cfg.get("MAX_TOKENS", 2000))

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_API_KEY:
    raise SystemExit("❌ Please set OPENROUTER_API_KEY in config.yaml")

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "http://localhost",  # OpenRouter requires these headers
    "X-Title": "Resume Parser",
    "Content-Type": "application/json",
}

# -------------------------
# Helpers: PDF reading
# -------------------------
def read_pdf(path: str) -> str:
    """Extract text from a text-based PDF using pdfminer."""
    text = extract_text(path)
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# -------------------------
# Schema & Prompts
# -------------------------
SCHEMA = {
    "full_name": "string",
    "email": "string",
    "phone": "string",
    "linkedin": "string",
    "education": [
        {"degree": "string", "institution": "string", "start_year": "string", "end_year": "string"}
    ],
    "experience": [
        {"company": "string", "title": "string", "start_year": "string", "end_year": "string", "description": "string"}
    ],
    "projects": [
        {"project_name": "string", "start_year": "string", "end_year": "string", "description": "string"}
    ],
    "technical_skills": ["string"],
    "certifications": ["string"],
    "languages": ["string"]
}

SYSTEM_INSTRUCTION = (
    "You are a professional resume parser. Given a resume text, extract the requested fields "
    "and RETURN ONLY valid JSON that exactly follows the schema described. "
    "If a field is not present, return an empty string or empty list. "
    "Do NOT include commentary or markdown — just JSON."
)

def build_user_prompt(resume_text: str) -> str:
    schema_json = json.dumps(SCHEMA, indent=2)
    return f"""
Parse the following resume text and output a VALID JSON object matching this schema:

Schema:
{schema_json}

Resume text:
\"\"\"{resume_text}\"\"\"

Constraints:
- Return only one valid JSON object, nothing else.
- Use empty strings or empty lists when a field is not found.
- Use YYYY for years if possible.
"""

# -------------------------
# OpenRouter API call
# -------------------------
def call_openrouter_chat(messages: list, model: str = MODEL, max_tokens: int = MAX_TOKENS, temperature: float = 0.0):
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    r = requests.post(OPENROUTER_CHAT_URL, json=payload, headers=HEADERS, timeout=120)

    # Debug: print status and raw text
    print("DEBUG STATUS:", r.status_code)
    print("DEBUG RESPONSE:", r.text[:50])  # print first 500 chars
    
    try:
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise Exception(f"OpenRouter API error {r.status_code}: {r.text}") from e


# -------------------------
# JSON extraction helpers
# -------------------------
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
            pass
    return None

def fix_json_with_model(prev_raw: str) -> Any:
    fix_system = (
        "You are a JSON fixer. Convert the following text into valid JSON matching the given schema. "
        "Return only JSON, no explanations."
    )
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
        raise ValueError("❌ No text was extracted from PDF. If scanned, run OCR first.")

    user_prompt = build_user_prompt(text)
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": user_prompt},
    ]

    print("-> Sending resume to model (this may take a few seconds)...")
    resp = call_openrouter_chat(messages)

    model_content = resp["choices"][0]["message"]["content"]
    parsed = extract_json_from_text(model_content)

    if parsed is not None:
        return parsed

    if retry_fix:
        print("⚠️ Model output was invalid JSON. Retrying with fixer...")
        fixed, raw = fix_json_with_model(model_content)
        return fixed or {"error": "Could not fix JSON", "raw_output": raw}

    return {"error": "Could not parse model output", "raw_output": model_content}

# -------------------------
# Run without argparse
# -------------------------
if __name__ == "__main__":
    print('using model: ', MODEL)
    # pdf_path = r"D:\Work\DevGate\CV Converter\test resume.pdf"
    pdf_path = r"D:\Work\DevGate\\CV Parser+Converter\\rana resume.pdf"
    result = parse_resume_with_openrouter(pdf_path, retry_fix=True)
    print(json.dumps(result, indent=2, ensure_ascii=False))
