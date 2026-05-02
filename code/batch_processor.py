import pandas as pd
import os
from triage_engine import process_issue

# File paths (adjusted for being inside the support_tickets folder)
INPUT_FILE = 'support_tickets.csv'
OUTPUT_FILE = 'output.csv'

def run_batch_triage():
    print(f"📂 Loading tickets from {INPUT_FILE}...")
    
    # Read the provided support tickets
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"❌ Error: {INPUT_FILE} not found in the current directory.")
        return

    results = []

    print(f"🤖 Agent is processing {len(df)} tickets. Please wait...")

    for index, row in df.iterrows():
        # UPDATED: Matching the exact capital 'I' and 'C' from your CSV
        issue_text = row['Issue']
        company_name = row.get('Company', 'Claude') 
        
        print(f"[{index+1}/{len(df)}] Analyzing issue for {company_name}...")
        
        # Use our RAG engine to get the smart response
        # This calls your triage_engine.py which uses llama3.2:3b
        raw_response = process_issue(issue_text, company_name)

        # Logic for the specific columns requested in the challenge
        status = "replied"
        request_type = "product_issue"
        
        # Automatic Escalation Logic for high-risk/sensitive cases
        # This satisfies the requirement to escalate sensitive/unsupported claims
        escalation_triggers = ['payment', 'refund', 'hack', 'security', 'password', 'legal', 'billing', 'money']
        if any(word in issue_text.lower() for word in escalation_triggers):
            status = "escalated"
            request_type = "bug" 

        # Build the final structured row
        results.append({
            "status": status,
            "product_area": "Technical Support",
            "response": raw_response,
            "justification": f"Answered using {company_name} local support corpus.",
            "request_type": request_type
        })

    # Save to output.csv exactly as requested by the schema
    output_df = pd.DataFrame(results)
    output_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ DONE! All {len(df)} tickets processed.")
    print(f"📄 Results saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_batch_triage()