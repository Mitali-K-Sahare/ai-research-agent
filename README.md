# 🔍 AI Research Agent

An AI-powered research agent that searches the web, reads sources, synthesizes findings, and generates structured research reports with confidence-rated claims.

Built with **LangGraph** (stateful workflows), **MCP** (interoperable tools), and **LangSmith** (observability).

## What It Does

Give it a topic. It will:

1. **Plan** — Generate targeted search queries using the LLM
2. **Search** — Find sources on the web using DuckDuckGo (free, no API key)
3. **Read** — Fetch and extract text from each web page
4. **Synthesize** — Combine findings into a structured report with confidence ratings
5. **Review** — Self-score the report quality (1-10). Below 7? Loops back for more sources
6. **Write** — Save the final report as a markdown file

## Architecture

```
START → Plan → Search ⟲ (loop) → Synthesize → Review → Write → END
                                                  ↓ (score < 7)
                                               Search (more sources)
```

**Why LangGraph (not a basic agent)?**
A basic agent (`create_react_agent`) gives the LLM full control — it might search once and declare victory. Our custom `StateGraph` enforces the workflow: plan first, search all queries, synthesize everything, review quality. The LLM operates within each step, but the graph controls what happens next.

## Project Structure

```
├── src/
│   ├── config.py          # Settings, API keys, LangSmith config
│   ├── prompts.py         # All system prompts in one place
│   ├── state.py           # TypedDict — the graph's shared memory
│   ├── tools.py           # 3 research tools (search, fetch, write)
│   ├── nodes.py           # 5 graph nodes (plan, search, synthesize, review, write)
│   ├── graph.py           # StateGraph assembly + conditional edges
│   └── mcp_server.py      # MCP server wrapping the same tools
├── run_research.py        # Terminal entry point
├── streamlit_app.py       # Web UI
├── verify_environment.py  # Environment checker
├── requirements.txt       # Dependencies
├── .env.example           # API key template
└── reports/               # Generated reports (auto-created)
```

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv genai_env
# Windows: genai_env\Scripts\activate
# Mac/Linux: source genai_env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API keys
cp .env.example .env
# Edit .env with your OPENAI_API_KEY (or GROQ_API_KEY for free alternative)

# 4. Verify everything works
python verify_environment.py
```

## Run

**Terminal mode:**
```bash
python run_research.py
# Or with a topic directly:
python run_research.py "Impact of AI on Indian healthcare"
```

**Web UI:**
```bash
streamlit run streamlit_app.py
```

**MCP server (for Claude Desktop, Cursor, etc.):**
```bash
mcp dev src/mcp_server.py
```

## Key Skills Demonstrated

- **LangGraph StateGraph** with custom nodes, conditional edges, and checkpointing
- **MCP (Model Context Protocol)** server exposing tools to any MCP client
- **LangSmith tracing** for full observability of every step
- **Confidence-rated claims** (VERIFIED / INFERRED / UNCERTAIN)
- **Self-review loop** where the agent evaluates its own output
- **Production patterns**: modular code, error handling, configurable settings

## Groq (Free Alternative)

To use Groq instead of OpenAI, follow the 3-line swap instructions in `src/config.py`.

## LangSmith Tracing

Set these in your `.env` file to enable automatic tracing:

```
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_your_key
LANGSMITH_PROJECT=research-agent
```

Every LLM call, tool invocation, and state update is traced automatically. View traces at [smith.langchain.com](https://smith.langchain.com).

---

*Built as Project 3 of the Applied GenAI Engineering Program.*
