import json
import pandas as pd
import re
from pathlib import Path

# Load audit report
base_dir = Path(__file__).resolve().parent.parent
audit_path = base_dir /'AI_models_dashboard'/ 'data' / 'audit_report.csv'
raw_data_path = base_dir /'AI_models_dashboard'/ 'data' / 'raw_data_lake.json'
audit_df = pd.read_csv(audit_path)

# Load raw data lake
with open(raw_data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Keywords that usually contain legal responsibility statements
legal_keywords = [
    "responsible",
    "not liable",
    "must comply",
    "prohibited",
    "not use",
    "own responsibility",
    "safety",
    "moderation",
    "accuracy"
]

def extract_legal_claim(text):
    """
    Extract the most relevant legal sentence
    from the policy text.
    """
    
    sentences = re.split(r'[.!?]', text)

    for sentence in sentences:
        for keyword in legal_keywords:
            if keyword in sentence.lower():
                return sentence.strip()

    return "No clear legal claim found"


# Build dictionary of company -> claim
company_claims = {}

for policy in data["company_policies"]:
    
    company = policy["company"]
    text = policy["text"]

    claim = extract_legal_claim(text)

    company_claims[company] = claim


def infer_company_from_model_name(model_name):
    """Infer company from model naming patterns so new models map automatically."""
    name = str(model_name).lower()

    explicit_map = {
        "mistral-7b": "Mistral AI",
        "mixtral": "Mistral AI",
        "flan-t5": "Google",
        "command-r": "Cohere",
        "claude": "Anthropic",
        "chatgpt": "OpenAI",
        "gpt": "OpenAI",
    }

    for token, company in explicit_map.items():
        if token in name:
            return company

    return None


# Create new column
legal_claims = []

for _, row in audit_df.iterrows():

    model = row["model_id"]

    company = infer_company_from_model_name(model)

    if company and company in company_claims:
        legal_claims.append(company_claims[company])
    else:
        legal_claims.append("Unknown")

audit_df["legal_claim"] = legal_claims


# Save updated CSV
audit_df.to_csv(audit_path, index=False)

print("[OK] legal_claim column successfully added!")