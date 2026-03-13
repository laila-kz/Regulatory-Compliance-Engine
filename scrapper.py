import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path

# -----------------------------
# 1️⃣ Target company policy URLs
# -----------------------------

policy_urls = {
    "Mistral AI": "https://legal.mistral.ai/terms/row-consumer-terms",
    "OpenAI": "https://openai.com/policies/terms-of-use/",
    "Anthropic": "https://www.anthropic.com/legal/consumer-terms",
    "Cohere": "https://cohere.com/terms-of-use",
    "Google": "https://ai.google.dev/gemini-api/terms"
}

# -----------------------------
# 2️⃣ Models to scrape (model cards / system cards)
# -----------------------------

model_urls = {
    "Mistral-7B": "https://huggingface.co/mistralai/Mistral-7B-v0.1",
    "Mixtral": "https://huggingface.co/mistralai/Mixtral-8x7B",
    "Flan-T5": "https://huggingface.co/google/flan-t5-base",
    "Command-R": "https://huggingface.co/CohereForAI/c4ai-command-r-v01",
    # Anthropic model/eval page has richer content than HF org overview.
    "Claude Sonnet": "https://www.anthropic.com/news/model-card-and-evaluation-for-claude-opus-4-and-claude-sonnet-4",
    # OpenAI system card page (acts as model safety card source).
    "ChatGPT (OpenAI)": "https://openai.com/index/gpt-4o-system-card/"
}

# -----------------------------
# Function to scrape page text
# -----------------------------

def scrape_page(url):

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract visible text
        text = soup.get_text(separator=" ", strip=True)

        return text[:20000]   # limit size

    except Exception as e:
        print("Error scraping:", url)
        return ""


# -----------------------------
# 3️⃣ Scrape policies
# -----------------------------

policies = []

for company, url in policy_urls.items():

    print("Scraping policy:", company)

    text = scrape_page(url)

    policies.append({
        "company": company,
        "url": url,
        "text": text
    })

    time.sleep(2)


# -----------------------------
# 4️⃣ Scrape model cards
# -----------------------------

models = []

for model, url in model_urls.items():

    print("Scraping model:", model)

    text = scrape_page(url)

    models.append({
        "model": model,
        "url": url,
        "text": text
    })

    time.sleep(2)


# -----------------------------
# 5️⃣ Save JSON
# -----------------------------

data_lake = {
    "company_policies": policies,
    "model_cards": models
}

# Save to data folder
base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / 'AI_models_dashboard' / 'data'
data_dir.mkdir(parents=True, exist_ok=True)
output_path = data_dir / 'raw_data_lake.json'

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data_lake, f, indent=2, ensure_ascii=False)

print(f"Data saved to: {output_path}")