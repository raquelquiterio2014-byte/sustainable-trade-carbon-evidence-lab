import json
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from core import calculate, validate_trade, digest, stable_json, is_public_http_url
from ai_gateway import analyze
from audit import connect, add_review, list_reviews

load_dotenv()
st.set_page_config(page_title="Sustainable Trade & Carbon Evidence Lab",page_icon="🌿",layout="wide")
st.markdown("""<style>
.stApp {background:linear-gradient(145deg,#061b15,#092c20 45%,#061810);color:#e8f7ee}
[data-testid="stSidebar"] {background:#09261c;border-right:1px solid #24563f}
[data-testid="stMetric"] {background:#103a2a;border:1px solid #28664b;border-radius:14px;padding:15px}
[data-testid="stMetricValue"] {color:#8ce3ac}
h1,h2,h3 {color:#b7f4c9!important}
div[data-testid="stTabs"] button {color:#d5f8e0}
.stButton button {background:#1a6848;color:white;border:1px solid #4a9b70}
.stButton button:hover {background:#25855d;color:white}
[data-testid="stDataFrame"] {border:1px solid #276347;border-radius:12px}
</style>""",unsafe_allow_html=True)
st.title("🌿 Sustainable Trade & Carbon Evidence Lab")
st.caption("COP31 AI Solutions Lab · Day 5 · Independent educational V1.0 · Synthetic examples ≠ verified carbon inventories")

@st.cache_data
def load_example():
    return pd.read_csv("data/sample_trade.csv").fillna("")

with st.sidebar:
    st.header("🌍 Evidence Controls")
    upload = st.file_uploader("Upload trade CSV (optional)",type=["csv"])
    st.info("All default trade records and emission factors are illustrative assumptions, not verified Brazilian sector factors.")
    st.caption("AI requires GEMINI_API_KEY. No AI call occurs until you click Analyze.")

try:
    df = pd.read_csv(upload).fillna("") if upload else load_example()
    problems = validate_trade(df)
except Exception as exc:
    st.error(f"Unable to read dataset: {exc}")
    st.stop()
if problems:
    st.error("Dataset validation failed: " + "; ".join(problems))
    st.stop()
calculated = calculate(df)
raw_bytes = df.to_csv(index=False).encode("utf-8")
data_hash = digest(raw_bytes)
tabs = st.tabs(["📊 Overview","🧮 Carbon Calculations","📚 Regulatory Evidence","🤖 AI Evidence Analyst","🛡️ Human Review & Audit"])
with tabs[0]:
    st.subheader("Trade & Carbon Overview")
    a,b,c,d = st.columns(4)
    a.metric("Transactions",len(calculated))
    b.metric("Product categories",calculated['product'].nunique())
    c.metric("Illustrative tCO₂e",f"{calculated.illustrative_total_tco2e.sum():,.1f}")
    d.metric("Synthetic records",int((calculated.evidence_status=='synthetic').sum()))
    st.plotly_chart(px.bar(calculated.groupby('product',as_index=False)['illustrative_total_tco2e'].sum(),x='product',y='illustrative_total_tco2e',color='product',color_discrete_sequence=['#43bd80','#a3d69b'],template='plotly_dark',title='Illustrative emissions by product (not certified)'),use_container_width=True)
    st.dataframe(calculated,use_container_width=True)
with tabs[1]:
    st.subheader("Deterministic Carbon Calculations")
    st.latex(r"E_{illustrative}=Q_{tonnes}\times EF_{production}+E_{transport}")
    st.write("Production factor: illustrative tCO₂e per tonne of product. Transport: illustrative absolute tCO₂e per transaction. No lifecycle boundary or CBAM embedded-emissions methodology is implied.")
    st.dataframe(calculated[['record_id','product','quantity_tonnes','production_tco2e_per_tonne','production_tco2e','transport_tco2e','illustrative_total_tco2e']],use_container_width=True)
    st.warning("Do not use these results for CBAM declarations, carbon credits, or regulatory compliance.")
with tabs[2]:
    st.subheader("Regulatory Evidence Library")
    sources=pd.read_csv('data/sources.csv').fillna('')
    st.dataframe(sources,use_container_width=True,hide_index=True)
    st.info("Source links are curated pointers, not a live regulatory update. Check consolidated EU law, amendments, current dates, sector scope, and competent authorities before making compliance claims.")
    st.markdown("**Evidence distinctions:** official legal text ≠ policy commentary; production emissions ≠ transport emissions; estimates ≠ verified product footprints; an AI summary ≠ legal advice.")
with tabs[3]:
    st.subheader("Gemini Evidence Extraction")
    st.write("Paste a short excerpt from an official document. The system does not scrape websites or retrieve PDFs automatically.")
    source_url=st.text_input("Public source URL",placeholder="https://...")
    excerpt=st.text_area("Exact source excerpt",height=180,placeholder="Paste text from the document here...")
    st.caption("Only the excerpt and URL are sent to the Gemini API when Analyze is clicked. Avoid confidential data.")
    if st.button("Analyze with real Gemini API",type="primary"):
        if not is_public_http_url(source_url):
            st.error("Provide a valid public HTTP(S) source URL")
        elif not excerpt.strip():
            st.error("Paste a source excerpt first")
        else:
            with st.spinner("Requesting Gemini analysis..."):
                try:
                    result=analyze(excerpt,source_url,os.getenv('GEMINI_MODEL','gemini-2.5-flash'))
                    st.session_state['ai_result']=result.model_dump()
                    st.session_state['ai_evidence_hash']=digest((source_url+'\n'+excerpt).encode())
                    st.success("API response received. Claims require human review.")
                except Exception as exc:
                    st.error(f"AI request failed: {exc}")
    if 'ai_result' in st.session_state:
        st.json(st.session_state['ai_result'])
        st.download_button("Download AI extraction JSON",json.dumps(st.session_state['ai_result'],indent=2,ensure_ascii=False),"ai_extraction.json","application/json")
with tabs[4]:
    st.subheader("Human Review & Audit Trail")
    st.code(f"Current dataset SHA-256: {data_hash}")
    st.caption("A reviewer decision records an assessment of evidence, not certified regulatory compliance.")
    con=connect()
    if 'ai_result' not in st.session_state:
        st.warning("Run an actual Gemini extraction first to enable review of AI output.")
    else:
        st.json(st.session_state['ai_result'])
        reviewer=st.text_input("Reviewer name or identifier")
        decision=st.selectbox("Decision",['needs_revision','approved','rejected'])
        notes=st.text_area("Review rationale / corrections")
        if st.button("Save human review"):
            try:
                ai_hash=digest(stable_json(st.session_state['ai_result']).encode())
                add_review(con,st.session_state['ai_evidence_hash'],ai_hash,decision,reviewer,notes)
                st.success("Review saved locally to SQLite")
            except Exception as exc:
                st.error(str(exc))
    rows=list_reviews(con)
    audit=pd.DataFrame(rows,columns=['id','created_utc','evidence_sha256','ai_output_sha256','decision','reviewer','notes'])
    st.dataframe(audit,use_container_width=True)
    st.download_button("Export audit CSV",audit.to_csv(index=False),"human_review_audit.csv","text/csv")
    st.download_button("Export calculated CSV",calculated.to_csv(index=False),"illustrative_trade_carbon.csv","text/csv")
    st.download_button("Export calculated JSON",calculated.to_json(orient='records',indent=2),"illustrative_trade_carbon.json","application/json")
    con.close()
st.divider()
st.caption("Evidence first. Engineering second. Measurable impact as the goal. | Educational prototype; no compliance certification.")
