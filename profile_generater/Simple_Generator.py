import os
import sys
from langchain_openai import ChatOpenAI

# ================= Configuration =================
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError(
        "OPENAI_API_KEY is not set. Please set it before running this script."
    )

MODEL_NAME = "gpt-4.1-nano"
INPUT_FILE = "gen_prompt.txt"
OUTPUT_FILE = "patient.txt"

def main():
    print(f"🚀 Raw Profile Generation (Model: {MODEL_NAME})")

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

    # 2. Initialize model
    llm = ChatOpenAI(model=MODEL_NAME, temperature=1.0)

    # 3. Send request directly
    print("⏳ Requesting OpenAI API...")
    try:
        response = llm.invoke(user_prompt)
        content = response.content
    except Exception as e:
        print(f"❌ API request failed: {e}")
        sys.exit()

    # 4. Save raw results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Generation complete! Content saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
