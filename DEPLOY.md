# Deploying to Streamlit Community Cloud

These steps assume you've unzipped `value-investor-ai.zip` somewhere on your
machine and have a terminal open in that folder.

## 1. Get a Google AI API key
If you don't already have one: go to https://aistudio.google.com/apikey,
sign in, and create a free API key. Keep it handy for step 5.

## 2. Push the code to a new GitHub repo

```bash
cd value-investor-ai
git init
git add .
git commit -m "Initial commit: value investing AI analyst demo"
```

Now create a new empty repo on GitHub:
1. Go to https://github.com/new
2. Repo name: e.g. `value-investing-ai-analyst`
3. Leave it **empty** (no README, no .gitignore, no license — you already have those)
4. Click **Create repository**

GitHub will show you a remote URL like `https://github.com/<you>/value-investing-ai-analyst.git`.
Back in your terminal:

```bash
git branch -M main
git remote add origin https://github.com/<you>/value-investing-ai-analyst.git
git push -u origin main
```

(If prompted for credentials, GitHub now requires a Personal Access Token
instead of your password — create one at
https://github.com/settings/tokens if you don't have one, or use
`gh auth login` if you have the GitHub CLI installed.)

## 3. (Optional) Test locally first

The app now self-bootstraps its vector store — `app/rag.py` will
automatically run the ingest step on first query if `vectorstore/` is
empty, so you don't need to commit a built vector store or run a separate
step before deploying. Still, it's worth a quick local smoke test:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export GOOGLE_API_KEY=your-key-here
streamlit run app/main.py
```

Open the local URL it prints, run one query, confirm it works, then `Ctrl+C`
and move to deployment.

## 4. Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with your GitHub account.
2. Click **Create app** (or **New app**).
3. Choose **Deploy a public app from GitHub**.
4. Pick your `value-investing-ai-analyst` repo, branch `main`, and set the
   main file path to `app/main.py`.
5. Click **Advanced settings** before deploying:
   - Under **Secrets**, add:
     ```
     GOOGLE_API_KEY = "your-key-here"
     ```
   - Python version: 3.11 (matches what this was built/tested against).
6. Click **Deploy**. First build takes a few minutes (installing
   `sentence-transformers`/`chromadb` is the slow part).

## 5. Verify

Once deployed, open the app URL Streamlit gives you, pick a company and a
skill, and run a query. Expand "Reasoning trace" to confirm RAG chunks and
MCP tool results are showing up — that confirms both the vector store and
the MCP subprocess (`mcp_server/stock_tools.py`) are working in the
deployed environment.

## Troubleshooting

- **App crashes on startup with a Chroma "collection not found" error** →
  the vector store wasn't committed/built. Re-check step 3.
- **MCP tool calls fail / time out** → Streamlit Cloud containers can be
  slow to spawn subprocesses on cold start; try the query again once the
  app has been running for a minute.
- **`GOOGLE_API_KEY` not found** → double check the secret is saved
  under the app's settings (not just typed and not saved), and that the
  key name matches exactly (`GOOGLE_API_KEY`).
