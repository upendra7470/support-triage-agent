import pandas as pd
import os
import datetime
import sys
from triage_engine import process_issue

# --- DYNAMIC PATHING ---
# Ensures logs go to the support_tickets folder, not hidden in the 'code' folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, 'support_tickets', 'manual_tickets_log.csv')

def start_interactive_session():
    print("\n" + "="*50)
    print("🚀 SENTINEL AI: MANUAL OVERRIDE STATION")
    print(f"📡 Logging active at: {LOG_FILE}")
    print("="*50)
    
    while True:
        issue = input("\n📝 Describe the customer's problem (or type 'exit'): ").strip()
        
        if issue.lower() in ['exit', 'quit', 'stop']: 
            print("\n👋 System shutting down. Have a productive day!")
            break
        
        if not issue:
            continue

        print("\n🏢 Select Organization Context:")
        print(" [1] HackerRank\n [2] Claude\n [3] Visa")
        choice = input("Selection (1-3): ").strip()
        
        company_map = {"1": "HackerRank", "2": "Claude", "3": "Visa"}
        company = company_map.get(choice, "General Context")

        print(f"\n🧠 Consulting {company} knowledge base...")
        
        # Pulling the response from our RAG brain
        try:
            answer = process_issue(issue, company)
        except Exception as e:
            print(f"❌ Brain Error: {e}")
            answer = "The system encountered an error processing this request."

        # Manual Safety Filters (Hard-coded escalation)
        payment_triggers = ['payment', 'money', 'refund', 'billing', 'charge', 'visa']
        if any(word in issue.lower() for word in payment_triggers):
            answer = "I've flagged this for our billing specialists. They will reach out to you directly."
            status = "escalated"
        else:
            status = "replied"

        print(f"\n✅ AI PROPOSED REPLY:\n{answer}")
        print("—"*50)

        # --- LOGGING ENGINE ---
        # We append every interaction so you have a history of your tests
        new_entry = {
            "timestamp": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "company": [company],
            "issue": [issue],
            "status": [status],
            "response": [answer]
        }
        
        try:
            df_log = pd.DataFrame(new_entry)
            file_exists = os.path.isfile(LOG_FILE)
            # 'a' mode appends; header=not file_exists ensures we only write columns once
            df_log.to_csv(LOG_FILE, mode='a', index=False, header=not file_exists)
            print(f"💾 Interaction cached to logs.")
        except Exception as log_err:
            print(f"⚠️ Warning: Could not save log entry: {log_err}")

if __name__ == "__main__":
    try:
        start_interactive_session()
    except KeyboardInterrupt:
        print("\n\n⚠️ Force closed by user. Exiting...")
        sys.exit(0)
