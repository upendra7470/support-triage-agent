import ollama
from utils import get_support_context

def process_issue(issue, company):
    # This pulls your local data for HackerRank, Claude, or Visa
    kb_context = get_support_context(company)

    # We tell Llama exactly who it is and what its goal is
    prompt = f"""
    You are an expert technical support specialist for {company}.
    Your knowledge base: {kb_context}
    
    Task: Solve the user's problem using only the facts above.
    If they ask "how-to", give clear, numbered steps.
    If the answer isn't in the context, use your general knowledge but stay professional.
    
    User Issue: {issue}
    Assistant:"""
    
    try:
        # Switching to the 3B model for instant speed on 8GB RAM
        response = ollama.chat(
            model='llama3.2:3b', 
            messages=[{'role': 'user', 'content': prompt}],
            options={
                'num_predict': 150, 
                'temperature': 0.2 # Lower temp = more accurate/less rambling
            }
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"Model Error: {str(e)}"