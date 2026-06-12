# MACA: Multi-Agent Clinical Auditor for Depression Simulation

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

MACA is a robust, multi-agent architecture designed to ensure clinical validity in depression patient simulations powered by Large Language Models (LLMs). 

Conventional single-agent simulations often suffer from "severity drift" and "symptom hallucination" (blindly conforming to leading questions to fabricate ungrounded symptoms). MACA resolves this by integrating real-time verification via an Auditor agent, utilizing a **Counterfactual Probability Gap (CPG)** metric to quantitatively suppress clinical hallucinations, and implementing **Dynamic Option Randomization** to eliminate LLM position biases.

## ✨ Key Features

* **Three-Agent Closed-Loop System**: 
  * **Agent A (Patient)**: Generates subjective BDI-II responses using Chain-of-Thought (CoT) self-explanation.
  * **Agent B (Auditor)**: Conducts strict two-track clinical audits (Direct Contradiction & Hallucination Detection).
  * **Agent C (Coach/Feedback)**: Provides targeted, persona-driven correction instructions.
* **Counterfactual Probability Gap (CPG)**: A quantitative mathematical metric that identifies ungrounded symptom hallucinations by measuring token probability shifts under counterfactual evidence.
* **Structural Debiasing**: Dynamically randomizes BDI-II option presentations to force semantic evaluation, effectively eliminating the LLM's inherent top-choice "position bias."
* **End-to-End Pipeline**: Includes automated scripts to dynamically generate diverse clinical patient profiles and conduct batch BDI-II assessments.

## 📂 Repository Structure

* **`profile_generater/`**: Module for generating simulated synthetic patient personas.
  * `Simple_Generator.py`: Script to generate a single raw patient profile (`patient.txt`) based on the instructions in `gen_prompt.txt`.
  * `Complex_Generator.py`: Automated batch generation script that continuously calls the LLM to generate a large dataset (e.g., 100 distinct profiles) and saves them into the output directory.
  * `gen_prompt.txt`: The base prompt template defining the target demographics, clinical stressor variables, and severity constraints.
  * `generated_patients/`: Directory where the batch-generated `.txt` patient profiles are saved.
* **`main.py`**: The main execution script. Handles batch processing, loops through patient profiles, tracks statistics, and exports results to CSV.
* **`maca_auditor.py`**: The core engine containing the `MACA_Counterfactual_Auditor` class. Manages LLM API calls, multi-agent interaction loops, and CPG calculations.
* **`prompts.py`**: Centralized LangChain prompt templates for all agents (Patient, Auditor, Coach) and the verification probe.
* **`config.py`**: Global configuration settings (Target model, severity thresholds, CPG thresholds, and clinical guidelines).
* **`utils.py`**: Utility functions for file handling and BDI-II questionnaire parsing (including the critical option shuffling mechanism).
* **`bdi_questions.txt`**: The standard 21-item Beck Depression Inventory-II (BDI-II) questionnaire dataset.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/MACA-Depression-Simulation.git](https://github.com/yourusername/MACA-Depression-Simulation.git)
   cd MACA-Depression-Simulation
