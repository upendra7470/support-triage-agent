import ollama
from utils import get_support_context

def process_issue(issue, company):
    """
    Core RAG logic: Fetches local context and queries Llama 3.2.
    Designed to be concise and fact-driven.
    """
    
    # Retrieval step: grabbing the .txt content for the specific company
    kb_context = get_support_context(company)

    # We use a structured prompt to keep the model from hallucinating
    # or getting too wordy.
    system_prompt = f"""
    [ROLE]
    You are a Tier 2 Technical Support Engineer for {company}.
    
    [KNOWLEDGE BASE]
    {kb_context}
    
    [INSTRUCTIONS]
    1. Answer the user issue strictly using the provided knowledge base facts.
    2. If the KB doesn't have the info, provide a professional general response.
    3. Use clear, bulleted or numbered steps for technical guides.
    4. Keep the tone helpful but efficient. No fluff.

    [USER ISSUE]
    {issue}

    [FINAL RESPONSE]
    """
    
    try:
        # Running llama3.2:3b - optimized for local 8GB Mac RAM
        response = ollama.chat(
            model='llama3.2:3b', 
            messages=[{'role': 'user', 'content': system_prompt}],
            options={
                'num_predict': 200,   # Slightly higher limit for detailed steps
                'temperature': 0.1,   # Near-zero temp for maximum consistency
                'top_p': 0.9          # Helps keep the response natural but focused
            }
        )
        
        # Clean up the output and return it to the processor
        return response['message']['content'].strip()
        
    except ConnectionError:
        return "ERROR: Ollama service is not responding. Is the local server running?"
    except Exception as e:
        # Human-style error logging
        print(f"DEBUG: Triage Engine Failure -> {e}")
        return "Technical processing error. Please escalate to a human agent."
