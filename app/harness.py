"""
The orchestrator ("harness") that ties skills, RAG, and MCP tools together
into a single grounded answer — and records a step-by-step trace so the UI
can show exactly what happened, which is the whole point of this demo.
"""

import os
import time

import anthropic

from app.rag import retrieve
from app.mcp_client import call_tool
from app.skills_loader import load_skills

MODEL = "claude-sonnet-4-5-20250929"

# Maps the company display name (as used in the RAG metadata / markdown H1)
# to the name the MCP stock tools understand.
COMPANY_TO_TICKER_NAME = {
    "Tata Consultancy Services (TCS.NS)": "TCS",
    "HDFC Bank (HDFCBANK.NS)": "HDFC Bank",
    "Asian Paints (ASIANPAINT.NS)": "Asian Paints",
    "ITC Limited (ITC.NS)": "ITC",
    "Titan Company (TITAN.NS)": "Titan",
}


def run_query(company_display_name: str, skill_id: str, user_question: str) -> dict:
    """Runs one query through the full harness and returns the answer + trace.

    Returns:
        {
          "answer": str,
          "trace": [ {"step": str, "detail": ...}, ... ],
        }
    """
    trace = []
    t0 = time.time()

    skills = load_skills()
    skill = skills.get(skill_id)
    if skill is None:
        raise ValueError(f"Unknown skill: {skill_id}")

    trace.append(
        {
            "step": "1. Skill selected",
            "detail": f"**{skill['name']}** — {skill['description']}",
        }
    )

    # --- RAG retrieval ---
    rag_chunks = []
    if skill["needs_rag"]:
        rag_chunks = retrieve(user_question, company_filter=company_display_name, k=4)
        trace.append(
            {
                "step": "2. RAG retrieval",
                "detail": [
                    f"[{c['company']} — {c['section']}] (relevance dist={c['distance']:.3f})"
                    for c in rag_chunks
                ]
                or ["No matching chunks found."],
            }
        )
    else:
        trace.append({"step": "2. RAG retrieval", "detail": "Skipped — not needed for this skill."})

    # --- MCP tool calls ---
    tool_results = {}
    ticker_name = COMPANY_TO_TICKER_NAME.get(company_display_name, company_display_name)
    for tool_name in skill["needs_tools"]:
        try:
            result = call_tool(tool_name, {"company": ticker_name})
            tool_results[tool_name] = result
            trace.append(
                {
                    "step": f"3. MCP tool call: {tool_name}",
                    "detail": result,
                }
            )
        except Exception as e:
            tool_results[tool_name] = {"error": str(e)}
            trace.append(
                {
                    "step": f"3. MCP tool call: {tool_name}",
                    "detail": f"Failed: {e}",
                }
            )

    # --- Assemble grounded prompt ---
    context_parts = []
    if rag_chunks:
        context_parts.append("### Retrieved filing excerpts:\n" + "\n\n".join(c["text"] for c in rag_chunks))
    if tool_results:
        context_parts.append("### Live market data (from MCP tools):\n" + str(tool_results))

    system_prompt = skill["prompt_template"].replace("{{company}}", company_display_name)
    context_block = "\n\n".join(context_parts) if context_parts else "(no external context retrieved)"

    user_message = (
        f"{context_block}\n\n"
        f"### User question:\n{user_question}"
    )

    trace.append({"step": "4. Assembled prompt", "detail": "Skill instructions + retrieved context + live data sent to Claude."})

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    answer = "".join(block.text for block in response.content if hasattr(block, "text"))

    trace.append({"step": "5. Answer generated", "detail": f"{time.time() - t0:.1f}s total"})

    return {"answer": answer, "trace": trace}
