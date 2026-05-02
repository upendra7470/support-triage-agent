import os
import glob

def get_support_context(company):
    """Retrieves relevant text from the data/ subfolders based on company name."""
    # Convert company to string to handle 'NaN' or float values
    safe_company = str(company).strip()
    
    # If the company is empty or 'None', we skip the knowledge search
    if not safe_company or safe_company.lower() in ['nan', 'none']:
        return ""

    context = ""
    # Path relative to support_tickets/ folder
    path = os.path.join("..", "data", safe_company.lower(), "*.txt")
    files = glob.glob(path)
    
    for f_path in files:
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                context += f"SOURCE: {os.path.basename(f_path)}\n{f.read()[:1500]}\n---\n"
        except Exception:
            continue
    return context