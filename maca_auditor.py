# maca_auditor.py
import json
import math
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import the configurations and prompts we extracted earlier
import config
import prompts

class MACA_Counterfactual_Auditor:
    def __init__(self, profile_text, severity_level):
        self.profile = profile_text
        self.severity = severity_level
        self.guideline = config.SEVERITY_GUIDELINES.get(severity_level, config.SEVERITY_GUIDELINES["Moderate"])
        
        # Agent A: Patient
        self.llm_a = ChatOpenAI(
            model=config.TARGET_MODEL, 
            temperature=0.8,
            model_kwargs={"response_format": {"type": "json_object"}}
        )
        
        # Agent B: Detector (Pure profile fact gatekeeper)
        self.llm_b_extractor = ChatOpenAI(
            model=config.TARGET_MODEL, 
            temperature=0.0,
            model_kwargs={"response_format": {"type": "json_object"}}
        )
        
        # Probe: Measures symptom confidence
        self.llm_probe = ChatOpenAI(
            model=config.TARGET_MODEL, 
            temperature=0.0,
            model_kwargs={"logprobs": True, "top_logprobs": 5} 
        )
        
        # Agent C: Coach
        self.llm_c = ChatOpenAI(model=config.TARGET_MODEL, temperature=0.5)

        self._build_prompts()

    def _build_prompts(self):
        # Assemble Agent A
        self.prompt_a = ChatPromptTemplate.from_messages([
            ("system", prompts.PROMPT_A_SYSTEM),
            ("human", prompts.PROMPT_A_HUMAN)
        ])

        # Assemble Agent B (Inject variables)
        sys_b = prompts.PROMPT_B_SYSTEM.format(sev_name=self.severity, sev_guide=self.guideline, profile="{profile}")
        self.prompt_b_extractor = ChatPromptTemplate.from_messages([
            ("system", sys_b),
            ("human", prompts.PROMPT_B_HUMAN)
        ])
        
        # Assemble Probe
        self.prompt_probe = ChatPromptTemplate.from_messages([
            ("system", prompts.PROMPT_PROBE_SYSTEM)
        ])

        # Assemble Agent C (Inject variables)
        sys_c = prompts.PROMPT_C_SYSTEM.format(sev_name=self.severity)
        self.prompt_c = ChatPromptTemplate.from_messages([
            ("system", sys_c),
            ("human", prompts.PROMPT_C_HUMAN)
        ])
        
        self.chain_a = self.prompt_a | self.llm_a | StrOutputParser()
        self.chain_b_extractor = self.prompt_b_extractor | self.llm_b_extractor | StrOutputParser()
        self.chain_c = self.prompt_c | self.llm_c | StrOutputParser()

    def _get_yes_probability(self, profile, symptom):
        prompt = self.prompt_probe.invoke({"profile": profile, "symptom": symptom})
        response = self.llm_probe.invoke(prompt)
        try:
            logprobs_data = response.response_metadata['logprobs']['content'][0]['top_logprobs']
            for token_data in logprobs_data:
                if token_data['token'].strip().lower() == 'yes':
                    return math.exp(token_data['logprob'])
            return 0.0
        except Exception:
            return 0.0

    def chat(self, bdi_question_text):
        feedback = "None"
        final_patient_data = {
            "score": 0, 
            "verbal_response": "Error", 
            "selected_option_text": "",
            "retries_needed": 0,
            "cf_triggered": False,
            "hallucinated_symptom": "None",
            "cpg_score": "N/A",
            "p_base": "N/A",
            "p_ce": "N/A"
        }
        
        for i in range(config.MAX_RETRIES + 1):
            final_patient_data["retries_needed"] = i
            
            # 1. Agent A Generation
            try:
                draft_str = self.chain_a.invoke({
                    "profile": self.profile, 
                    "question": bdi_question_text, 
                    "feedback": feedback
                }).replace("```json", "").replace("```", "").strip()
                draft_data = json.loads(draft_str)
                
                final_patient_data.update({
                    "score": draft_data.get("score", 0),
                    "verbal_response": draft_data.get("verbal_response", ""),
                    "selected_option_text": draft_data.get("selected_option_text", "")
                })
            except Exception:
                feedback = "OUTPUT FORMAT ERROR: You must output valid JSON."
                continue
                
            verbal_response = draft_data.get("verbal_response", "")
            
            if i == 0: print("")
            print(f"   [Draft {i+1}] Score: {draft_data.get('score')} | Reply: {verbal_response}")
            
            # 2. Agent B Detection and Auditing
            try:
                b_out = self.chain_b_extractor.invoke({
                    "profile": self.profile, 
                    "score": draft_data.get("score"), 
                    "response": verbal_response
                })
                b_data = json.loads(b_out)
            except Exception as e:
                print(f"      [Debug] Agent B Error: {type(e).__name__} - {str(e)}")
                b_data = {"is_contradiction": False, "has_potential_hallucination": False}
            
            is_contradiction = b_data.get("is_contradiction", False)
            has_hallucination = b_data.get("has_potential_hallucination", False)
            
            # [Track 1]: Direct contradiction audit
            if is_contradiction:
                reasoning = b_data.get("contradiction_reason", "Contradicts explicit profile facts.")
                print(f"   [Audit {i+1}] ❌ FAIL (Contradiction) | {reasoning}")
                critique = f"Your response blatantly contradicts your profile: {reasoning}. Please correct your option and verbal response to align strictly with your profile facts."
                
            # [Track 2]: CPG Counterfactual probe verification
            elif has_hallucination:
                symptom = b_data.get("hallucinated_symptom", "")
                cf_profile = b_data.get("counterfactual_profile", "")
                
                p_base = self._get_yes_probability(self.profile, symptom)
                p_ce = self._get_yes_probability(cf_profile, symptom)
                cpg = abs(p_base - p_ce)
                
                print(f"   [Adversarial Check] '{symptom}' | CPG: {cpg:.4f} (Base:{p_base:.2f}, CF:{p_ce:.2f})")
                
                final_patient_data.update({
                    "cf_triggered": True,
                    "hallucinated_symptom": symptom,
                    "cpg_score": round(cpg, 4),
                    "p_base": round(p_base, 4),
                    "p_ce": round(p_ce, 4)
                })
                
                if cpg >= config.CPG_THRESHOLD:
                    print(f"   [Audit {i+1}] ✅ PASS | Symptom verified by CF-Test.")
                    return final_patient_data
                else:
                    print(f"   [Audit {i+1}] ❌ FAIL (Hallucination) | Low CPG. LLM hallucination detected.")
                    critique = f"You mentioned '{symptom}' which is NOT supported by your profile facts. Please choose a different option (likely 0) and remove this hallucinated symptom."
            
            # Passed all checks
            else:
                print(f"   [Audit {i+1}] ✅ PASS | Aligns with Profile and no ungrounded symptoms detected.")
                return final_patient_data
                
            # 3. Agent C Correction
            if i < config.MAX_RETRIES:
                feedback = self.chain_c.invoke({"critique": critique})
                print(f"   🔧 [Coach] {feedback}")
            else:
                print(f"   ⚠️ Max retries reached.")
                return final_patient_data
                
        return final_patient_data