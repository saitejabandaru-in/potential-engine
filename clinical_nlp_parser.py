"""
Potential Engine — Clinical NLP Parser
Implements Named Entity Recognition (NER) and rule-based Negation Detection
for extracting medical observations, conditions, and drug dosages.
"""

import re

class ClinicalNLPParser:
    def __init__(self):
        # Patterns for extraction
        self.condition_pattern = re.compile(
            r'\b(necrotizing fasciitis|sepsis|appendicitis|cellulitis|diabetic ketoacidosis|pneumonia|myocardial infarction)\b', 
            re.IGNORECASE
        )
        self.drug_pattern = re.compile(
            r'\b(vancomycin|piperacillin|tazobactam|insulin|aspirin|metformin|ibuprofen)\b', 
            re.IGNORECASE
        )
        self.dosage_pattern = re.compile(
            r'\b(\d+\s*(mg|g|mcg|ml|units|units/hr|mg/kg))\b', 
            re.IGNORECASE
        )
        # Negation triggers (preceding terms)
        self.negation_triggers = [
            "no", "denies", "negative for", "without", "rules out", "ruled out", 
            "absence of", "never had", "no signs of"
        ]

    def is_negated(self, text, entity_start_idx):
        """
        Check if the entity at entity_start_idx is negated by preceding text.
        """
        pre_context = text[max(0, entity_start_idx - 30):entity_start_idx].lower()
        for trigger in self.negation_triggers:
            if re.search(r'\b' + re.escape(trigger) + r'\b\s*$', pre_context) or                re.search(r'\b' + re.escape(trigger) + r'\b[^.!?]*$', pre_context):
                return True
        return False

    def parse_note(self, text):
        parsed_entities = []
        
        # 1. Extract conditions
        for match in self.condition_pattern.finditer(text):
            condition = match.group(0)
            start_idx = match.start()
            negated = self.is_negated(text, start_idx)
            parsed_entities.append({
                "type": "condition",
                "value": condition,
                "negated": negated,
                "start": start_idx
            })
            
        # 2. Extract drugs and dosages
        for match in self.drug_pattern.finditer(text):
            drug = match.group(0)
            start_idx = match.start()
            # Look for dosage immediately following drug
            post_context = text[start_idx:start_idx + 40]
            dosage_match = self.dosage_pattern.search(post_context)
            dosage = dosage_match.group(0) if dosage_match else "unspecified"
            
            parsed_entities.append({
                "type": "medication",
                "value": drug,
                "dosage": dosage,
                "start": start_idx
            })
            
        return parsed_entities

if __name__ == "__main__":
    clinical_note = (
        "Patient presents with no signs of necrotizing fasciitis. "
        "However, there is concern for early sepsis. "
        "Initiated Vancomycin 1.25g IV stat and Metformin 500 mg daily."
    )
    
    parser = ClinicalNLPParser()
    entities = parser.parse_note(clinical_note)
    
    print("Parsed Clinical Entities:")
    for ent in entities:
        if ent["type"] == "condition":
            status = "NEGATED" if ent["negated"] else "CONFIRMED"
            print(f"  [Condition] {ent['value']} -> Status: {status}")
        elif ent["type"] == "medication":
            print(f"  [Medication] {ent['value']} -> Dosage: {ent['dosage']}")
