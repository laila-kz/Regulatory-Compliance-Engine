import json
import os
import pandas as pd
from pathlib import Path


def load_json_with_fallbacks(json_file):
    with open(json_file, 'rb') as f:
        raw_bytes = f.read()

    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return json.loads(raw_bytes.decode(encoding))
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError:
            continue

    raise ValueError(f"Could not decode or parse JSON file: {json_file}")


def flatten_model_data(json_file):
    raw_data = load_json_with_fallbacks(json_file)

    cleaned_rows = []

    # Support multiple raw_data schemas:
    # 1) {model_id: {metadata, full_text}}, 2) {"model_cards": [...]}, 3) [...]
    if isinstance(raw_data, dict) and "model_cards" in raw_data and isinstance(raw_data["model_cards"], list):
        records = raw_data["model_cards"]
    elif isinstance(raw_data, list):
        records = raw_data
    elif isinstance(raw_data, dict):
        records = []
        for model_id, content in raw_data.items():
            if isinstance(content, dict):
                enriched = dict(content)
                enriched.setdefault("model", model_id)
                records.append(enriched)
    else:
        records = []

    for content in records:
        if not isinstance(content, dict):
            continue

        model_id = content.get("model") or content.get("model_id") or content.get("id") or "unknown"
        metadata = content.get('metadata', {})
        if not isinstance(metadata, dict):
            metadata = {}

        full_text = content.get('full_text') or content.get('text') or ""
        full_text_lower = full_text.lower()

        # We extract specific fields that map to EU AI Act Requirements
        row = {
            "model_id": model_id,
            "license": metadata.get("license", "unknown"),
            "datasets": ", ".join(metadata.get("datasets", [])),
            "language": ", ".join(metadata.get("language", [])),
            # Article 13: Transparency Check (looking for keywords in text)
            "has_limitations_section": 1 if "limitations" in full_text_lower else 0,
            "has_bias_discussion": 1 if "bias" in full_text_lower else 0,
            "has_risks_discussion": 1 if "risks" in full_text_lower or "hazards" in full_text_lower else 0,
            # Article 10: Data Governance (looking for data source transparency)
            "data_transparency_score": len(metadata.get("datasets", [])),
            "raw_text": full_text
        }
        cleaned_rows.append(row)
    
    return pd.DataFrame(cleaned_rows)

# Create your clean 'Warehouse'
base_dir = Path(__file__).resolve().parent.parent
raw_data_path = base_dir /'AI_models_dashboard'/ 'data' / 'raw_data_lake.json'
df = flatten_model_data(str(raw_data_path))
print(df.head())

# Export cleaned data for downstream analysis
data_dir = base_dir / 'AI_models_dashboard' / 'data'
data_dir.mkdir(parents=True, exist_ok=True)
output_path = data_dir / 'clean_model_cards.csv'
df.to_csv(output_path, index=False, encoding='utf-8')
print(f"Saved cleaned data to: {output_path}")