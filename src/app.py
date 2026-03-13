import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --- 1. Page Config & Theming ---
logo_path = Path(__file__).resolve().parents[1] / "media" / "Logo.png"
st.set_page_config(page_title="RegTech AI Auditor 2026", page_icon=str(logo_path), layout="wide")

# Custom CSS for the "Glassmorphism" Dark Theme
st.markdown("""
    <style>
    :root {
        --bg-main: #0e1117;
        --card-bg: #161b22;
        --card-border: #2f3b52;
        --title-cyan: #F8F9FA;
    }
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    }
    .stAlert { border-radius: 12px; }
    h1, h2, h3 {
        color: var(--title-cyan) !important;
        text-shadow: 0 1px 10px rgba(125, 226, 255, 0.22);
    }
    .chart-card {
        background: linear-gradient(160deg, rgba(22, 27, 34, 0.95), rgba(15, 22, 35, 0.95));
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 12px;
        box-shadow: 0 10px 26px rgba(0, 0, 0, 0.35);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Data Loading ---
# @st.cache_data
# def load_data():
#     # Loading your provided CSV structure
#     df = pd.read_csv("../data/audit_report.csv")
#     return df

import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # 1. Get the path to the 'src' folder where this app.py lives
    current_script_path = os.path.abspath(__file__)
    src_folder = os.path.dirname(current_script_path)
    
    # 2. Go up one level to the Project Root, then into the 'data' folder
    project_root = os.path.dirname(src_folder)
    file_path = os.path.join(project_root, "data", "audit_report.csv")
    
    # 3. Check if the file actually exists before reading (prevents crash)
    if not os.path.exists(file_path):
        st.error(f"File not found at: {file_path}")
        # Optional: return an empty dataframe so the rest of the app doesn't break
        return pd.DataFrame()
        
    return pd.read_csv(file_path)

df = load_data()

# --- 3. Header & KPI Section ---
header_logo, header_text = st.columns([0.11, 0.89])
with header_logo:
    if logo_path.exists():
        st.image(str(logo_path), width=90)
with header_text:
    st.title("Regulatory Compliance Engine")
    st.markdown("### 2026 EU AI Act Surveillance: Technical Reality vs. Legal Claims")

# KPI Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_models = len(df)
avg_risk = df['risk_score'].mean()
non_compliant = len(df[df['risk_score'] > 0])
aligned_percent = (len(df[df['compliance_status'].str.contains('Aligned', na=False)]) / total_models) * 100

kpi1.metric("Models Audited", total_models)
kpi2.metric("Avg Risk Score", f"{avg_risk:.1f}", delta="-2.1", delta_color="inverse")
kpi3.metric("Critical Gaps", non_compliant, help="Models missing Article 13 Transparency sections")
kpi4.metric("Legal Alignment", f"{aligned_percent:.0f}%")

st.divider()

# --- 4. Main Analytics Row ---
col_charts_left, col_charts_right = st.columns([1.2, 1])

with col_charts_left:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.subheader("📊 Transparency Gap Analysis")
    # Horizontal bar for better readability of model names
    fig_risk = px.bar(
        df, 
        x='risk_score', 
        y='model_id', 
        orientation='h',
        color='risk_score',
        color_continuous_scale='Reds',
        title="Risk Score by Model (Higher = Less Transparent)",
        template="plotly_dark"
    )
    fig_risk.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_risk, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_charts_right:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.subheader("⚖️ Compliance Status Distribution")
    # Donut chart for status
    status_counts = df['compliance_status'].value_counts()
    fig_donut = px.pie(
        names=status_counts.index, 
        values=status_counts.values, 
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template="plotly_dark"
    )
    fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. Deep Dive Audit Logs ---
st.divider()
st.subheader("🔎 Detailed Audit & Legal Comparison")

# Search and Filter
search_query = st.text_input("Search model documentation...", placeholder="e.g. Mistral, Google, Safety")
if search_query:
    display_df = df[df['model_id'].str.contains(search_query, case=False) | df['raw_text'].str.contains(search_query, case=False)]
else:
    display_df = df

# Styled Dataframe
st.dataframe(
    display_df[['model_id', 'risk_score', 'compliance_status', 'risk_flags', 'legal_claim']],
    column_config={
        "risk_score": st.column_config.ProgressColumn("Risk Level", min_value=0, max_value=40, format="%d"),
        "legal_claim": st.column_config.TextColumn("Corporate Legal Claim", width="large"),
        "risk_flags": "Audit Detection"
    },
    use_container_width=True,
    hide_index=True
)

# --- 6. Footer Methodology ---
st.divider()
with st.expander("🛠️ Audit Methodology & Regulatory Framework"):
    st.write("""
    **Framework:** EU AI Act 2026 (Articles 10, 13, and 52).
    
    **Audit Logic:** 1. **Data Ingestion:** Automated scraping of Hugging Face Model Cards and Corporate /legal subdirectories.
    2. **Transparency Scoring:** Models are penalized (-15 points) for missing structured 'Bias', 'Risks', or 'Limitations' sections.
    3. **Legal Alignment:** Natural Language Inference (NLI) is used to detect contradictions between technical 'No Moderation' notices and legal 'Safe for Use' claims.
    """)
