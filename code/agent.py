import ollama
import pandas as pd
import json
import re
import os
import sys

# --- CONFIG ---
# Using 2B for speed on local Mac hardware
MODEL = "gemma2:2b" 
# We use dynamic paths so the script doesn't break if run from different folders
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'support_tickets', 'support_tickets.csv')
OUTPUT_FILE = os.path.join(BASE_DIR, 'support_tickets', 'output.csv')

def extract_json_payload(text):
    """
    Scrub the AI response to find the JSON block. 
    AI models love to talk before giving the actual data!
    """
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except Exception as e:
        print(f"Internal JSON Parse Error: {e}")
        return None

def run_triage_engine(issue, subject, company):
    # HARD-CODED SECURITY CHECK
    # Real-world safety: Always escalate money or security stuff before the AI even sees it.
    flags = ['money', 'refund', 'fraud', 'stolen', 'hacked', 'security', 'identity', 'visa']
    is_urgent = any(word in str(issue).lower() for word in flags)

    # Building the context for the model
    instructions = f"""
    ROLE: Senior Technical Support Lead
    OBJECTIVE: Categorize this ticket and provide a helpful response.
    
    DATA:
    - Subject: {subject}
    - Organization: {company}
    - Content: {issue}

    JSON FORMAT REQUIRED:
    {{
      "status": "replied/escalated",
      "product_area": "string",
      "response": "Short professional reply",
      "justification": "Why this choice?",
      "request_type": "bug/feature_request/product_issue"
    }}

    {"[!] FLAG: Financial/Security context detected. Set status to escalated." if is_urgent else ""}
    """
    
    try:
        # Calling Ollama - fingers crossed for a clean JSON response
        raw_output = ollama.chat(model=MODEL, messages=[{'role': 'user', 'content': instructions}])
        parsed = extract_json_payload(raw_output['message']['content'])
        if parsed:
            return parsed
    except Exception as err:
        print(f"Ollama Connection Error: {err}")

    # Safety net: If the AI fails or timeouts, we escalate by default
    return {
        "status": "escalated",
        "product_area": "General Triage",
        "response": "We've received your request and a specialist is looking into it.",
        "justification": "System fallback triggered.",
        "request_type": "product_issue"
    }

def start_processing():
    print(f"--- 🤖 Sentinel-Triage v1.0 (Engine: {MODEL}) ---")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Can't find the file at {INPUT_FILE}")
        sys.exit(1)

    print(f"📂 Loading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    
    # Fill in the blanks if the CSV is messy
    df['Subject'] = df.get('Subject', 'No Subject Provided')
    df['Company'] = df.get('Company', 'Internal')
    
    processed_data = []
    print(f"⏳ Processing {len(df)} tickets... please wait.")

    for i, row in df.iterrows():
        # Visual progress bar for the human at the keyboard
        print(f"[{i+1}/{len(df)}] Analyzing: {row['Subject'][:30]}...")
        result = run_triage_engine(row['Issue'], row['Subject'], row['Company'])
        processed_data.append(result)
    
    # Dump everything to the final CSV
    pd.DataFrame(processed_data).to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ SUCCESS: Results written to {OUTPUT_FILE}")

if __name__ == "__main__":
    start_processing()
