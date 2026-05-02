import os
import glob

def get_support_context(company):
    """
    Retrieves internal documentation for a specific company to provide
    context for the RAG engine.
    """
    # 1. Clean up the input - humans sometimes pass messy data!
    target = str(company).strip().lower()
    
    if not target or target in ['nan', 'none', 'unknown']:
        return "No specific company context available."

    # 2. DYNAMIC PATHING
    # This finds the 'data' folder relative to this script's location
    # so it works on any computer.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_folder = os.path.join(project_root, 'data', target)

    context_parts = []
    
    # 3. SEARCHING THE KNOWLEDGE BASE
    if os.path.exists(data_folder):
        # We look for all text files in the company's subfolder
        search_pattern = os.path.join(data_folder, "*.txt")
        kb_files = glob.glob(search_pattern)

        for file_path in kb_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # We only take a snippet to avoid hitting token limits
                    snippet = content[:2000] 
                    filename = os.path.basename(file_path)
                    context_parts.append(f"REFERENCE [{filename}]:\n{snippet}")
            except Exception as e:
                print(f"   ⚠️ Skipping file {file_path}: {e}")
                continue
    else:
        print(f"   ⚠️ Warning: No data folder found for '{target}' at {data_folder}")

    # Join all found documents with a clear separator
    if not context_parts:
        return "Generic Support Mode: No local knowledge base found."
        
    return "\n\n---\n\n".join(context_parts)

if __name__ == "__main__":
    # Quick debug test for the developer
    print("Testing Utils...")
    test_context = get_support_context("Visa")
    print(f"Context Length: {len(test_context)} chars")
