#We are going to build a "Risk Classifier" that reads the raw_text and decides if the model is High-Risk based on the 2026 legal definitions.
# -----------------------------
# NLP Analysis / Risk Auditor
# -----------------------------

import json
import pandas as pd
from pathlib import Path

# 1️⃣ Load your clean dataset
base_dir = Path(__file__).resolve().parent.parent
csv_path = base_dir /'AI_models_dashboard'/ 'data' / 'clean_model_cards.csv'
df = pd.read_csv(csv_path)

# 2️⃣ Define High-Risk Sectors (from EU AI Act 2026 Annex III)
high_risk_sectors = [
    'medical', 
    'recruitment', 
    'biometric', 
    'police', 
    'credit', 
    'education', 
    'judicial'
]


def load_expected_model_ids(raw_json_path):
    """Return model IDs from raw_data_lake.json, preserving order."""
    try:
        with open(raw_json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    model_ids = []
    for card in raw_data.get("model_cards", []):
        if isinstance(card, dict):
            model_id = card.get("model") or card.get("model_id") or card.get("id")
            if model_id:
                model_ids.append(str(model_id))

    # Deduplicate while preserving order.
    return list(dict.fromkeys(model_ids))

# 3️⃣ Auditor Function: Calculate Compliance Risk
def calculate_compliance_risk(row):
    """
    Calculates a risk score based on:
    - High-risk sector mentions
    - Lack of moderation mechanisms
    - Missing bias discussion (transparency)
    """
    text = str(row['raw_text']).lower()
    score = 0
    flags = []

    # Check High-Risk Sector Mentions
    for sector in high_risk_sectors:
        if sector in text:
            score += 25
            flags.append(f"Sector Mention: {sector}")

    # Check for lack of moderation
    if "no moderation" in text or "no moderation mechanisms" in text:
        score += 40
        flags.append("Violation: No Moderation Mechanisms")

    # Check for transparency / missing bias discussion
    # Assume your CSV has a column 'has_bias_discussion' with 0 or 1
    if 'has_bias_discussion' in row and row['has_bias_discussion'] == 0:
        score += 15
        flags.append("Transparency: Missing Bias Section")

    return pd.Series([score, ", ".join(flags)])


# 4️⃣ Apply Auditor to the dataset
df[['risk_score', 'risk_flags']] = df.apply(calculate_compliance_risk, axis=1)

# 5️⃣ Create Audit Report (sorted by highest risk)
audit_report = df[['model_id', 'risk_score', 'risk_flags']].sort_values(
    by='risk_score', ascending=False
)

# 5.1️⃣ Reconcile with raw_data_lake so pipeline never drops scraped models
raw_data_path = base_dir /'AI_models_dashboard'/ 'data' / 'raw_data_lake.json'
expected_model_ids = load_expected_model_ids(raw_data_path)
existing_ids = set(audit_report['model_id'].astype(str).tolist())
missing_ids = [m for m in expected_model_ids if m not in existing_ids]

if missing_ids:
    filler = pd.DataFrame(
        {
            'model_id': missing_ids,
            'risk_score': [0] * len(missing_ids),
            'risk_flags': ['No audit signals detected'] * len(missing_ids),
        }
    )
    audit_report = pd.concat([audit_report, filler], ignore_index=True)
    print(f"[INFO] Reconciled {len(missing_ids)} missing model(s) from raw_data_lake.json")

# 6️⃣ Save audit report to CSV for dashboard / further analysis
audit_report_path = base_dir /'AI_models_dashboard'/ 'data' / 'audit_report.csv'
audit_report.to_csv(audit_report_path, index=False)

# 7️⃣ Optional: print top 10 highest risk models
print("=== Top 10 High-Risk Models ===")
print(audit_report.head(10))