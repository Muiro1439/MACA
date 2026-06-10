# utils.py
import random

def load_file(path):
    """Reads the specified local text file."""
    try:
        with open(path, 'r', encoding='utf-8') as f: 
            return f.read()
    except FileNotFoundError:
        print(f"⚠️ Warning: File '{path}' not found.")
        return "File Not Found."

def parse_bdi_questions(bdi_text):
    """Parses the BDI-II questionnaire text, splits it into separate questions, and randomly shuffles the options."""
    items = []
    blocks = [block.strip() for block in bdi_text.split('---') if block.strip()]
    
    for block in blocks:
        # Split by line and filter out any empty lines
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        
        if not lines:
            continue
            
        title = lines[0]      # The first line is always the title
        options = lines[1:]   # All remaining lines are the options
        
        # Core step: Randomly shuffle the order of the options
        random.shuffle(options)
        
        # Concatenate the title and the shuffled options back into a single plain text block
        shuffled_text = f"{title}\n" + "\n".join(options)
        
        items.append({
            "title": title,
            "full_text": shuffled_text
        })
        
    return items