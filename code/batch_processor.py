import pandas as pd
import os
import sys
# Import the RAG logic from your triage_engine
from triage_engine import process_issue

def run_batch_triage():
    # --- AUTOMATIC PATH LOCATOR ---
    # This finds the 'support_tickets' folder relative to where this script lives
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(base_dir, 'support_tickets', 'support_tickets.csv')
    output_path = os.path.join(base_dir, 'support_tickets', 'output.csv')

    print("--- 🚀 Sentinel Batch Triage Engine ---")
    
    # Safety check: Does the file actually exist?
    if not os.path.exists(input_path):
        print(f"❌ Error: CSV not found at {input_path}")
        print("Please ensure support_tickets.csv is inside the support_tickets folder.")
        return

    print(f"📂 Loading: {input_path}")
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"❌ Failed to read CSV: {e}")
        return

    results = []
    total_tickets = len(df)
    print(f"🤖 Processing {total_tickets} tickets using Llama 3.2 RAG...")

    for index, row in df.iterrows():
        # Clean up data from the CSV
        issue_text = str(row.get('Issue', ''))
        company_name = str(row.get('Company', 'General'))
        
        print(f"[{index+1}/{total_tickets}] Analyzing: {company_name} issue...")
        
        # Call the RAG engine
        try:
            raw_response = process_issue(issue_text, company_name)
        except Exception as e:
            print(f"   ⚠️ RAG Error: {e}")
            raw_response = "System error during processing. Escalated to human."

        # Logic for Status & Request Type
        status = "replied"
        request_type = "product_issue"
        
        # Hard-coded Escalation Logic (The "Human" touch)
        urgent_triggers = ['payment', 'refund', 'hack', 'security', 'password', 'money', 'visa']
        if any(word in issue_text.lower() for word in urgent_triggers):
            status = "escalated"
            request_type = "bug" 

        # Build the final output row
        results.append({
            "status": status,
            "product_area": "Technical Support",
            "response": raw_response,
            "justification": f"Processed via {company_name} knowledge base.",
            "request_type": request_type
        })

    # Save to the output file
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_path, index=False)
    
    print(f"\n✅ DONE! All {total_tickets} tickets triaged.")
    print(f"📄 Final Results saved to: {output_path}")

if __name__ == "__main__":
    run_batch_triage()
