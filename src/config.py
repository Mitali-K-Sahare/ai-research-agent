"""
=============================================================================
Project 3: AI Research Agent
config.py — Central Configuration (Single Source of Truth)
=============================================================================

WHAT THIS FILE DOES:
  Every setting the project needs lives here — API keys, model selection,
  research parameters, and LangSmith tracing. Change something once here,
  it changes everywhere.

WHY ONE FILE:
  Scattering settings across files leads to bugs. "Which file has the model
  name? Did I update the temperature in both places?" One file, no confusion.

GROQ SWAP:
  To switch from OpenAI to Groq (free), follow the 3-line swap instructions
  below. Everything else stays the same.
=============================================================================
"""

# ── IMPORTS ─────────────────────────────────────────────────────────────────

# os.getenv() reads environment variables (like API keys)
import os

# load_dotenv() reads the .env file and loads its values into environment variables
# Without this, os.getenv("OPENAI_API_KEY") would return None
from dotenv import find_dotenv, load_dotenv

# ChatOpenAI is LangChain's wrapper for talking to OpenAI (and Groq via base_url)
# This is the same class used in Week 5, 6, 8, and Project 2
from langchain_openai import ChatOpenAI

# ── Load the .env file ─────────────────────────────────────────────────────
# This must happen BEFORE any os.getenv() calls
load_dotenv(find_dotenv())


# ============================================================
# LLM SETUP — The AI model that powers the agent
# ============================================================

# --- OPTION 1: OpenAI (Primary — Recommended) ---
# gpt-4o-mini is fast, cheap, and good enough for research tasks
# temperature=0.3 keeps responses focused but allows some creativity

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_API_KEY"),
)

# --- OPTION 2: Groq (Free Alternative — 3-Line Swap) ---
# To use Groq instead of OpenAI:
#   1. Comment out the 4 lines above (llm = ChatOpenAI... through the closing paren)
#   2. Uncomment the 5 lines below
#   3. Make sure GROQ_API_KEY is set in your .env file
#
# llm = ChatOpenAI(
#     base_url="https://api.groq.com/openai/v1",
#     model="llama-3.3-70b-versatile",
#     temperature=0.3,
#     api_key=os.getenv("GROQ_API_KEY"),
# )


# ============================================================
# RESEARCH SETTINGS
# ============================================================

# How many search queries the planner should generate per topic
# 3 gives good coverage without burning too many API calls
MAX_SEARCH_QUERIES = 3

# Maximum search iterations before we stop and synthesize
# This is the safety limit — prevents the agent from searching forever
# Even if the review says "need more", we stop after this many iterations
MAX_SEARCH_ITERATIONS = 5

# How many DuckDuckGo results to fetch per search query
# 3 results per query × 3 queries = up to 9 sources total
SEARCH_RESULTS_PER_QUERY = 3

# Maximum characters to extract from each web page
# Web pages can be 50,000+ characters. We take the first 3,000
# to keep context windows manageable and costs down
MAX_CONTENT_LENGTH = 3000

# Minimum review score (out of 10) to accept the report
# Below this → the agent loops back to search for more sources
# 7 is a reasonable threshold — strict enough to catch thin reports,
# lenient enough to not loop forever
MIN_REVIEW_SCORE = 7


# ============================================================
# FILE PATHS
# ============================================================

# Where generated research reports are saved
# The write_node creates this folder if it doesn't exist
REPORTS_DIR = "reports"


# ============================================================
# LANGSMITH TRACING (Observability)
# ============================================================
# LangSmith reads these automatically from your .env file:
#   LANGSMITH_TRACING=true
#   LANGSMITH_API_KEY=lsv2_...
#   LANGSMITH_PROJECT=research-agent
#
# Once set, EVERY LLM call, tool invocation, and state update
# is traced automatically — no extra code needed.
#
# View traces at: https://smith.langchain.com
# ============================================================
