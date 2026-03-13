import pandas as pd
from pathlib import Path

# Load audit report
base_dir = Path(__file__).resolve().parent.parent
audit_path = base_dir /'AI_models_dashboard'/ 'data' / 'audit_report.csv'
df = pd.read_csv(audit_path)


# Keywords that imply a company promises safety
safety_claim_keywords = [
    "safety",
    "responsible",
    "comply",
    "policy",
    "prohibited",
    "guidelines"
]


def legal_claim_mentions_safety(text):

    text = str(text).lower()

    for word in safety_claim_keywords:
        if word in text:
            return True

    return False


conflict_results = []

for _, row in df.iterrows():

    legal_claim = row["legal_claim"]
    risk_flags = row["risk_flags"]

    claim_safety = legal_claim_mentions_safety(legal_claim)

    # logic gate
    if claim_safety and isinstance(risk_flags, str) and "No Moderation" in risk_flags:
        conflict_results.append(" Compliance Conflict")

    elif claim_safety:
        conflict_results.append(" Aligned")

    else:
        conflict_results.append("Unknown")


df["compliance_status"] = conflict_results


# Save updated dataset
df.to_csv(audit_path, index=False)

print("[OK] Conflict detection complete!")