import pandas as pd
import os
import sys

# Import your RAG engine
try:
    from triage_engine import process_issue
except ImportError:
    # If the import fails, we try to add the current directory to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from triage_engine import process_issue

def run_batch_triage():
    # --- BULLETPROOF PATH LOGIC ---
    # 1. Get the absolute path of THIS script (batch_processor.py)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Go up one level to the main project folder
    project_root = os.path.dirname(script_dir)
    
    # 3. Look for the CSV in the support_tickets folder at the root
    input_path = os.path.join(project_root, 'support_tickets', 'support_tickets.csv')
    output_path = os.path.join(project_root, 'support_tickets', 'output.csv')

    print(f"--- 🚀 AI Batch Processor Started ---")
    print(f"🔍 Searching for CSV at: {input_path}")

    if not os.path.exists(input_path):
        # EMERGENCY FALLBACK: If root search fails, look in the same folder as script
        input_path = os.path.join(script_dir, 'support_tickets.csv')
        output_path = os.path.join(script_dir, 'output.csv')
        
        if not os.path.exists(input_path):
            print("❌ CRITICAL ERROR: support_tickets.csv not found anywhere!")
            print(f"Please move your CSV to: {os.path.join(project_root, 'support_tickets/')}")
            return

    print(f"✅ Found file! Reading data...")
    df = pd.read_csv(input_path)

    results = []
    print(f"🤖 Processing {len(df)} tickets...")

    for index, row in df.iterrows():
        issue_text = str(row.get('Issue', ''))
        company_name = str(row.get('Company', 'General'))
        
        print(f"[{index+1}/{len(df)}] Analyzing {company_name}...")
        
        # Get AI Response
        try:
            response_text = process_issue(issue_text, company_name)
        except:
            response_text = "Technical error. Manual triage required."

        # Triage Logic
        status = "replied"
        req_type = "product_issue"
        
        urgent = ['payment', 'refund', 'hack', 'security', 'money', 'visa']
        if any(word in issue_text.lower() for word in urgent):
            status = "escalated"
            req_type = "bug"

        results.append({
            "status": status,
            "product_area": "Technical Support",
            "response": response_text,
            "justification": f"Automated RAG response for {company_name}.",
            "request_type": req_type
        })

    # Save results
    pd.DataFrame(results).to_csv(output_path, index=False)
    print(f"\n✨ DONE! Results saved to: {output_path}")

if __name__ == "__main__":
    run_batch_triage()
