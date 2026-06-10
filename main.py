# main.py
import os
import sys
import csv
import config
from utils import load_file, parse_bdi_questions
from maca_auditor import MACA_Counterfactual_Auditor

if __name__ == "__main__":
    print("⏳ Loading BDI-II questions...")
    bdi_text = load_file(config.FILES["bdi"])
    if "File Not Found." in bdi_text:
        print("❌ Error: Missing BDI-II txt file. Exiting.")
        sys.exit(1)
        
    bdi_items = parse_bdi_questions(bdi_text)
    print(f"✅ Successfully loaded {len(bdi_items)} BDI-II questions.")
    
    if not os.path.exists(config.PATIENTS_DIR):
        print(f"❌ Error: Patient directory '{config.PATIENTS_DIR}' not found.")
        sys.exit(1)
        
    patient_files = [f for f in os.listdir(config.PATIENTS_DIR) if f.endswith(".txt")]
    if not patient_files:
        print(f"❌ Error: No .txt files found in '{config.PATIENTS_DIR}'.")
        sys.exit(1)

    print(f"✅ Found {len(patient_files)} patient profiles.")
    print("\n" + "="*60)
    print(f"🏥 MACA Automated BDI-II Batch Assessment ({config.TARGET_SEVERITY})")
    print("="*60)

    # Global log list
    all_results_log = [] 

    # ================= Statistics Tracker (New) =================
    stats = {
        "total_patients": len(patient_files),
        "target_match_count": 0,            # Number of patients successfully matching the target severity
        "total_questions": len(patient_files) * len(bdi_items),
        "first_try_pass": 0,                # Number of questions passed directly with 0 retries
        "corrected_pass": 0,                # Number of questions passed after 1-2 retries
        "failed_questions": 0               # Number of questions that still failed after reaching MAX_RETRIES
    }

    # ================= 🚀 Outer Loop: Iterate through each patient =================
    for p_idx, p_file in enumerate(patient_files):
        profile_path = os.path.join(config.PATIENTS_DIR, p_file)
        
        print(f"\n" + "#"*60)
        print(f"👤 [Patient {p_idx+1}/{stats['total_patients']}] Processing: {p_file}")
        print("#"*60)
        
        profile_text = load_file(profile_path)
        bot = MACA_Counterfactual_Auditor(profile_text, config.TARGET_SEVERITY)
        total_bdi_score = 0
        
        # ================= 🎯 Inner Loop: Test each BDI question =================
        for idx, item in enumerate(bdi_items):
            title = item["title"]
            full_question = item["full_text"]
            
            print(f"\n▶️ [{p_file}] [Question {idx+1}/{len(bdi_items)}] {title}")
            print("-" * 40)
            
            result_data = bot.chat(full_question)
            score = result_data.get("score", 0)
            retries = result_data.get("retries_needed", 0)
            
            total_bdi_score += score
            
            # Record question-level statistics
            if retries == 0:
                stats["first_try_pass"] += 1
            elif retries < config.MAX_RETRIES:
                stats["corrected_pass"] += 1
            else:
                stats["failed_questions"] += 1

            all_results_log.append({
                "Patient_File": p_file,
                "Item": title,
                "Final_Score": score,
                "Patient_Response": result_data.get("verbal_response", "Error"),
                "Retries_Needed": retries,
                "CF_Triggered": result_data.get("cf_triggered", False),
                "Tested_Symptom": result_data.get("hallucinated_symptom", "None"),
                "P_Base": result_data.get("p_base", "N/A"),
                "P_CE": result_data.get("p_ce", "N/A"),
                "CPG_Score": result_data.get("cpg_score", "N/A")
            })
            
        # Calculate the clinical interpretation for the current patient
        interpretation = "Normal"
        if 14 <= total_bdi_score <= 19:
            interpretation = "Mild Depression"
        elif 20 <= total_bdi_score <= 28:
            interpretation = "Moderate Depression"
        elif total_bdi_score >= 29:
            interpretation = "Severe Depression"
            
        is_match = interpretation.split()[0].lower() == config.TARGET_SEVERITY.lower()
        if is_match:
            stats["target_match_count"] += 1

        print(f"\n✅ {p_file} Assessment Complete.")
        print(f"📊 BDI-II Score: {total_bdi_score} ({interpretation}) | Target Match: {'Yes' if is_match else 'No'}")

    # ================= 💾 Batch Export to Global CSV =================
    csv_filename = f"MACA_Batch_Results_{config.TARGET_SEVERITY}.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=all_results_log[0].keys())
        writer.writeheader()
        writer.writerows(all_results_log)
    
    # ================= 📈 Print Global Statistics Report (New) =================
    match_rate = (stats["target_match_count"] / stats["total_patients"]) * 100
    perfect_rate = (stats["first_try_pass"] / stats["total_questions"]) * 100
    recovery_rate = (stats["corrected_pass"] / stats["total_questions"]) * 100
    failure_rate = (stats["failed_questions"] / stats["total_questions"]) * 100
    
    print("\n" + "="*60)
    print(f"🏆 ALL ASSESSMENTS COMPLETE - STATISTICAL SUMMARY")
    print("="*60)
    print(f"👥 Total Patients Tested:      {stats['total_patients']}")
    print(f"🎯 Target Match Rate (Pass %): {match_rate:.1f}% ({stats['target_match_count']}/{stats['total_patients']})")
    print("-" * 60)
    print(f"📝 Total Questions Asked:      {stats['total_questions']}")
    print(f"✅ First-Try Pass Rate:        {perfect_rate:.1f}% ({stats['first_try_pass']})")
    print(f"🔧 Corrected Pass Rate:        {recovery_rate:.1f}% ({stats['corrected_pass']})")
    print(f"❌ Failed (Max Retries):       {failure_rate:.1f}% ({stats['failed_questions']})")
    print("="*60)
    print(f"💾 Comprehensive batch data strictly saved to: {csv_filename}")
    print("="*60)