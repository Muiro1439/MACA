import os
import sys
from langchain_openai import ChatOpenAI

# ================= Configuration =================
# ⚠️ Enter your API Key
os.environ["OPENAI_API_KEY"] = "" 

# Model settings (Strictly keeping your original settings)
MODEL_NAME = "gpt-4.1-nano"  
INPUT_FILE = "gen_prompt.txt"

# Automation settings
NUM_GENERATIONS = 100               
OUTPUT_DIR = "generated_patients"  

def main():
    print(f"🚀 Automated Batch Profile Generation (Model: {MODEL_NAME})")

    # 1. Read Prompt
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            user_prompt = f.read().strip()
    except FileNotFoundError:
        print(f"❌ Error: File not found {INPUT_FILE}")
        sys.exit()

    if not user_prompt:
        print("❌ Error: Prompt file is empty")
        sys.exit()

    # Create the output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 2. Initialize model
    llm = ChatOpenAI(model=MODEL_NAME, temperature=1.0)

    print(f"⏳ Starting generation loop for {NUM_GENERATIONS} profiles...\n")

    # 3. Automation Loop
    for i in range(1, NUM_GENERATIONS + 1):
        output_file = os.path.join(OUTPUT_DIR, f"patient_{i}.txt")
        print(f"▶️ [{i}/{NUM_GENERATIONS}] Requesting OpenAI API...")
        
        try:
            # Send request directly
            response = llm.invoke(user_prompt)
            content = response.content
            
            # 4. Save raw results iteratively
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"  ✅ Generation complete! Saved to: {output_file}")
            
        except Exception as e:
            print(f"  ❌ API request failed for iteration {i}: {e}")

    print(f"\n🎉 All {NUM_GENERATIONS} profiles generated successfully in the '{OUTPUT_DIR}' folder!")

if __name__ == "__main__":
    main()