import pandas as pd
import os
import datetime
from triage_engine import process_issue

# The file you want to check for your logs
LOG_FILE = 'manual_tickets_log.csv'

def start_agent():
    print("\n🚀 AI AGENT STATION: ONLINE")
    print("Logs saving to: manual_tickets_log.csv")
    
    while True:
        issue = input("\n📝 Enter customer issue: ").strip()
        if issue.lower() == 'exit': 
            print("👋 Session ended.")
            break
        
        print("🏢 [1] HackerRank | [2] Claude | [3] Visa")
        choice = input("Selection: ").strip()
        company_map = {"1": "HackerRank", "2": "Claude", "3": "Visa"}
        company = company_map.get(choice, "Unknown")

        print("⚡ AI Thinking...")
        
        # Get the direct answer from the brain
        answer = process_issue(issue, company)

        # Payment Logic
        payment_keywords = ['payment', 'money', 'refund', 'billing', 'charge']
        if any(k in issue.lower() for k in payment_keywords):
            answer = "Our customer support will reach out shortly regarding your payment concern."
            status = "escalated"
        else:
            status = "replied"

        print(f"\n✅ AI REPLY:\n{answer}\n" + "—"*40)

        # --- LOGGING TO CSV ---
        log_data = {
            "timestamp": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "company": [company],
            "issue": [issue],
            "status": [status],
            "response": [answer]
        }
        
        df_log = pd.DataFrame(log_data)
        
        # Check if file exists to handle headers
        file_exists = os.path.isfile(LOG_FILE)
        df_log.to_csv(LOG_FILE, mode='a', index=False, header=not file_exists)
        
        print(f"💾 Interaction logged successfully.")

if __name__ == "__main__":
    start_agent()