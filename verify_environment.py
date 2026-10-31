"""
=============================================================================
Project 3: AI Research Agent
verify_environment.py — Check That Everything Is Installed Correctly
=============================================================================

HOW TO RUN:
  python verify_environment.py

  This checks every import the project needs and reports what's missing.
  Run this BEFORE trying to run the agent.
=============================================================================
"""

import sys

print("=" * 60)
print("  Project 3: AI Research Agent — Environment Check")
print("=" * 60)
print()
print("Python version:", sys.version)
print()

# Track results
passed = 0
failed = 0
total = 0


def check_import(package_name, import_statement):
    """Try an import and report success or failure."""
    global passed, failed, total
    total = total + 1
    try:
        exec(import_statement)
        print("  ✅", package_name)
        passed = passed + 1
    except ImportError as error:
        print("  ❌", package_name, "—", str(error))
        failed = failed + 1


# ── Core LangChain ──────────────────────────────────────────────────────
print("--- Core LangChain ---")
check_import("langchain", "import langchain")
check_import("langchain-core", "from langchain_core.messages import HumanMessage")
check_import("langchain-openai", "from langchain_openai import ChatOpenAI")

# ── LangGraph ───────────────────────────────────────────────────────────
print("\n--- LangGraph ---")
check_import("langgraph", "from langgraph.graph import StateGraph")
check_import("langgraph checkpoint", "from langgraph.checkpoint.memory import MemorySaver")

# ── Search & Web ────────────────────────────────────────────────────────
print("\n--- Search & Web Scraping ---")
check_import("duckduckgo-search", "from duckduckgo_search import DDGS")
check_import("requests", "import requests")
check_import("beautifulsoup4", "from bs4 import BeautifulSoup")

# ── MCP ─────────────────────────────────────────────────────────────────
print("\n--- MCP ---")
check_import("mcp", "from mcp.server.fastmcp import FastMCP")

# ── Streamlit ───────────────────────────────────────────────────────────
print("\n--- Streamlit ---")
check_import("streamlit", "import streamlit")

# ── Utilities ───────────────────────────────────────────────────────────
print("\n--- Utilities ---")
check_import("python-dotenv", "from dotenv import load_dotenv")

# ── API Key Check ───────────────────────────────────────────────────────
print("\n--- API Key Check ---")
total = total + 1
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if api_key and api_key != "your_openai_api_key_here":
    print("  ✅ OPENAI_API_KEY is set")
    passed = passed + 1
else:
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and groq_key != "your_groq_api_key_here":
        print("  ✅ GROQ_API_KEY is set (using Groq)")
        passed = passed + 1
    else:
        print("  ❌ No API key found — set OPENAI_API_KEY or GROQ_API_KEY in .env")
        failed = failed + 1

# ── Summary ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
if failed == 0:
    print("  ✅ ALL CHECKS PASSED (" + str(passed) + "/" + str(total) + ")")
    print("  You're ready to run: python run_research.py")
else:
    print("  ❌ " + str(failed) + " CHECK(S) FAILED")
    print("  Fix the issues above, then run this script again.")
    print("  Tip: pip install -r requirements.txt")
print("=" * 60)
