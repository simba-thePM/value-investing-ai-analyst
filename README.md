# Value Investing AI Analyst — Indian Equities

A small demo app that showcases four AI-engineering concepts working
together: **Skills**, **MCP**, **RAG**, and an orchestration **harness** —
applied to a genuinely useful, narrow domain: value-investing analysis of a
handful of NSE-listed Indian companies (TCS, HDFC Bank, Asian Paints, ITC,
Titan).

Ask a question, pick an analysis "skill," and the app shows not just the
answer but the full reasoning trace: which skill was chosen, which filing
excerpts were retrieved (RAG), which live market data was pulled (MCP), and
how it was all assembled into the final Claude prompt.

## Architecture

```
User question + company + skill
        │
        ▼
   app/harness.py  (orchestrator)
        │
        ├─► app/skills_loader.py   → loads skills/*.md (prompt templates)
        ├─► app/rag.py             → retrieves from Chroma vector store
        │                             (built from data/annual_reports/*.md)
        ├─► app/mcp_client.py      → calls mcp_server/stock_tools.py
        │                             over the real MCP protocol (stdio)
        └─► anthropic SDK          → Claude generates the grounded answer
        │
        ▼
   app/main.py (Streamlit UI) — shows answer + step-by-step trace
```

- **Skills** (`skills/*.md`): four markdown files with YAML frontmatter,
  each defining an analysis mode — Buffett-style qualitative checklist,
  Graham-number intrinsic value estimate, red-flags audit, and an ELI10
  explainer.
- **RAG** (`data/annual_reports/*.md` + `app/ingest.py` + `app/rag.py`):
  illustrative filing excerpts for 5 companies, chunked by section, embedded
  locally with `sentence-transformers`, and stored in a local Chroma vector
  store. **Replace these markdown files with real annual report PDFs**
  (parsed via `pypdf`) for genuine analysis — the sample corpus is written
  to resemble real filing content but is not sourced from actual filings.
- **MCP** (`mcp_server/stock_tools.py`): a real MCP server exposing
  `get_stock_price` and `get_financial_ratios` tools backed by `yfinance`
  (NSE tickers, `.NS` suffix). `app/mcp_client.py` is a genuine MCP client
  that launches the server as a subprocess and talks to it over the actual
  MCP stdio protocol — the server file itself could be dropped into Claude
  Desktop or any other MCP host unmodified.
- **Harness** (`app/harness.py`): the orchestrator that ties it all
  together and records a trace object the UI renders.

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Set your Anthropic API key. Copy `.env.example` to `.env` and fill it
   in, or export it directly:

   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```

   (Get a key at https://console.anthropic.com — the app uses
   `claude-sonnet-4-5-20250929` by default; change `MODEL` in
   `app/harness.py` if you want a different model.)

3. Build the RAG vector store (run once, and again any time you edit files
   in `data/annual_reports/`):

   ```bash
   python app/ingest.py
   ```

4. Run the app:

   ```bash
   streamlit run app/main.py
   ```

## Customizing

- **Add a company**: drop a new `data/annual_reports/<name>.md` file
  (same `# Title` / `## Section` structure as the existing ones), add its
  ticker to `COMPANY_TO_TICKER_NAME` in `app/harness.py`, re-run
  `python app/ingest.py`.
- **Add a skill**: create a new `skills/<id>.md` with YAML frontmatter
  (`id`, `name`, `description`, `needs_rag`, `needs_tools`) and a prompt
  template body. It'll show up in the UI automatically.
- **Add an MCP tool**: add a new `@mcp.tool()`-decorated function to
  `mcp_server/stock_tools.py`, then reference its name in a skill's
  `needs_tools` list.

## Deployment

This is a standard Streamlit app, so any of these work well for a free/cheap
portfolio demo:

- **Streamlit Community Cloud** (easiest): push this repo to GitHub, connect
  it at share.streamlit.io, set `ANTHROPIC_API_KEY` as a secret in the app
  settings. The app self-bootstraps its vector store on first query if
  `vectorstore/` is empty, so no separate ingest step is required at
  deploy time. See `DEPLOY.md` for a full walkthrough.
- **Render / Fly.io**: deploy as a standard Python web service; set the
  start command to `streamlit run app/main.py --server.port=$PORT
  --server.address=0.0.0.0` and set `ANTHROPIC_API_KEY` as an environment
  variable.

## Known limitations (by design, to keep this a weekend-scoped demo)

- The RAG corpus is a small, hand-curated illustrative sample for 5
  companies, not real ingested annual report PDFs — swap in real filings
  for genuine analysis.
- `yfinance` is a free, unofficial data source suitable for a demo, not for
  production trading decisions.
- The MCP client spins up a fresh subprocess per tool call rather than
  keeping a long-lived session open — fine at demo scale, would want
  optimizing for higher traffic.
- Nothing here is investment advice — it's a demonstration of AI
  engineering patterns, not a stock-picking tool.
