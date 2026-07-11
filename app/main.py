"""
Streamlit UI for the Value Investing AI Analyst — a demo app showcasing
Skills, MCP, RAG, and an orchestration harness applied to Indian equities.

Run with:
    streamlit run app/main.py
"""

import os
import sys

import streamlit as st

# Allow `python -m` style absolute imports (app.harness etc.) whether this
# file is run directly by `streamlit run` or as a module.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.harness import run_query, COMPANY_TO_TICKER_NAME
from app.skills_loader import load_skills

st.set_page_config(page_title="Value Investing AI Analyst (India)", page_icon="📈", layout="wide")

st.title("📈 Value Investing AI Analyst — Indian Equities")
st.caption(
    "A demo app combining **Skills**, **MCP**, **RAG**, and an orchestration **harness** "
    "to answer value-investing questions about a handful of NSE-listed companies, grounded in "
    "their actual filings and live market data."
)

if not os.environ.get("ANTHROPIC_API_KEY"):
    st.warning(
        "Set the `ANTHROPIC_API_KEY` environment variable before running queries. "
        "See the README for setup instructions.",
        icon="⚠️",
    )

skills = load_skills()
companies = list(COMPANY_TO_TICKER_NAME.keys())

col1, col2 = st.columns(2)
with col1:
    company = st.selectbox("Company", companies)
with col2:
    skill_id = st.selectbox(
        "Analysis skill",
        options=list(skills.keys()),
        format_func=lambda sid: skills[sid]["name"],
    )

st.caption(f"*{skills[skill_id]['description']}*")

default_questions = {
    "buffett_checklist": "Does this business have a durable competitive advantage worth paying up for?",
    "intrinsic_value": "Is this stock roughly fairly valued right now?",
    "red_flags": "Are there any red flags I should worry about before investing?",
    "eli10": "What does this company do and why might it be a good investment?",
}

question = st.text_area(
    "Your question",
    value=default_questions.get(skill_id, ""),
    height=80,
)

run = st.button("Analyze", type="primary")

if run:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("Missing ANTHROPIC_API_KEY — set it and reload the app.")
    else:
        with st.spinner("Running skill → RAG retrieval → MCP tool calls → Claude..."):
            try:
                result = run_query(company, skill_id, question)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                result = None

        if result:
            st.subheader("Answer")
            st.markdown(result["answer"])

            with st.expander("🔍 Reasoning trace — see exactly what the harness did", expanded=False):
                for step in result["trace"]:
                    st.markdown(f"**{step['step']}**")
                    detail = step["detail"]
                    if isinstance(detail, list):
                        for item in detail:
                            st.markdown(f"- {item}")
                    elif isinstance(detail, dict):
                        st.json(detail)
                    else:
                        st.markdown(str(detail))
                    st.divider()

st.markdown("---")
with st.sidebar:
    st.header("How this demo works")
    st.markdown(
        """
**Skills** — markdown-defined analysis modes (`skills/*.md`) such as a
Buffett-style checklist, a Graham-number valuation, a red-flags audit, and
an ELI10 explainer. Pick one above.

**RAG** — company filing excerpts (`data/annual_reports/*.md`) are chunked
and embedded into a local Chroma vector store, then retrieved per-question
so answers are grounded in real filing language, not just model priors.

**MCP** — `mcp_server/stock_tools.py` is a real MCP server exposing live
NSE stock price and fundamental-ratio tools via yfinance. The harness talks
to it over the actual MCP protocol (stdio transport).

**Harness** — `app/harness.py` orchestrates all of the above: picks the
skill, retrieves context, calls tools, assembles a grounded prompt, and
calls Claude. Expand "Reasoning trace" above to see every step.
        """
    )
    st.caption("Data for the 5 companies is an illustrative sample corpus — swap in real annual report PDFs for production use.")
