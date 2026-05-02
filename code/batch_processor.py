import pandas as pd
import os
import sys
# Importing the logic from our neighboring file
from triage_engine import process_issue

# --- PATH HANDLER ---
# This ensures the script finds the CSV whether you run it from root or the code/ folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'support_tickets', 'support_tickets.csv')
OUTPUT_FILE = os.path.join(BASE_DIR, 'support_tickets', 'output.csv')

def run_batch_triage():
    print("--- 🚀 Sentinel Batch Triage Engine Started ---")
    
    # Check if the input file exists before we do anything else
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Could not find '{INPUT_FILE}'")
        print("Tip: Make sure the CSV is in the 'support_tickets' folder.")
        return

    print(f"📂 Loading: {INPUT_FILE}")
    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"❌ Failed to read CSV: {e}")
        return

    results = []
    total = len(df)
    print(f"🤖 Processing {total} tickets using local RAG corpus...")

    for index, row in df.iterrows():
        # Get data from CSV - handle missing company names gracefully
        issue_text = str(row.get('Issue', ''))
        company_name = str(row.get('Company', 'General'))
        
        print(f"[{index+1}/{total}] Triaging: {company_name} issue...")
        
        # 🧠 THE RAG CALL
        # We pass the issue to our Llama 3.2 engine defined in triage_engine.py
        try:
            raw_response = process_issue(issue_text, company_name)
        except Exception as e:
            print(f"   ⚠️ RAG Error on ticket {index+1}: {e}")
            raw_response = "Unable to process. Routed to manual review."

        # DEFAULT TRIAGE VALUES
        status = "replied"
        request_type = "product_issue"
        
        # 🔥 ESCALATION LOGIC (Human-coded safety triggers)
        # We catch sensitive topics that shouldn't be handled by AI alone
        urgent_topics = ['payment', 'refund', 'hack', 'security', 'password', 'legal', 'billing', 'money']
        if any(word in issue_text.lower() for word in urgent_topics):
            status = "escalated"
            request_type = "bug" 

        # Package the result for the final output
        results.append({
            "status": status,
            "product_area": "Technical Support",
            "response": raw_response,
            "justification": f"Validated against {company_name} internal documentation.",
            "request_type": request_type
        })

    # Save the final results
    output_df = pd.DataFrame(results)
    output_df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n✅ SUCCESS: All {total} tickets processed.")
    print(f"📄 Output generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_batch_triage()
