# config.py
import os

# ================= Credentials =================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise EnvironmentError(
        "OPENAI_API_KEY is not set. Please set it before running the project."
    )


# ================= Model & System Settings =================
TARGET_MODEL = "gpt-4o-mini"  
TARGET_SEVERITY = "Moderate"     
MAX_RETRIES = 3              
CPG_THRESHOLD = 0.2          

# ================= External File Configuration =================
FILES = {
    "bdi": "bdi_questions.txt"  
}
PATIENTS_DIR = "profile_generater/generated_patients"  

# ================= Severity Definitions =================
SEVERITY_GUIDELINES = {
    "Healthy":  "No signs of depression. Positive tone, engaged, hopeful.",
    "Mild":     "Low-level sadness or fatigue. Can still function but feels 'off'. Not suicidal. complaining but polite.",
    "Moderate": "Clear functional impairment. Visible distress. Sentences may be shorter. Negative outlook. 'I can't work well'.",
    "Severe":   "Intense suffering. Hopelessness. Suicidal ideation. May be unresponsive or extremely brief. 'Everything is black'."
}