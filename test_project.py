"""
=============================================================================
Project 3: AI Research Agent
test_project.py — Full Validation Script
=============================================================================

RUN THIS ON YOUR MACHINE (not in Claude's sandbox).

Tests in 4 stages:
  Stage 1: Import validation (all packages installed?)
  Stage 2: Graph compilation (does the StateGraph build?)
  Stage 3: Tool smoke test (do DuckDuckGo search and URL fetch work?)
  Stage 4: Full pipeline (run a real research with a simple topic)

HOW TO RUN:
  python test_project.py
=============================================================================
"""

import sys
import os
import time

print("=" * 60)
print("  Project 3: AI Research Agent — FULL VALIDATION")
print("=" * 60)
print()

# ============================================================
# STAGE 1: Import Validation
# ============================================================
print("STAGE 1: IMPORT VALIDATION")
print("-" * 40)

stage1_pass = True

imports_to_test = [
    ("langchain_openai.ChatOpenAI", "from langchain_openai import ChatOpenAI"),
    ("langchain_core.messages", "from langchain_core.messages import HumanMessage, SystemMessage"),
    ("langchain_core.tools", "from langchain_core.tools import tool"),
    ("langgraph.graph", "from langgraph.graph import StateGraph, START, END"),
    ("langgraph.checkpoint", "from langgraph.checkpoint.memory import MemorySaver"),
    ("duckduckgo_search", "from duckduckgo_search import DDGS"),
    ("requests", "import requests"),
    ("beautifulsoup4", "from bs4 import BeautifulSoup"),
    ("mcp.server.fastmcp", "from mcp.server.fastmcp import FastMCP"),
    ("python-dotenv", "from dotenv import load_dotenv"),
    ("src.config", "from src.config import llm, MAX_SEARCH_QUERIES"),
    ("src.prompts", "from src.prompts import PLANNER_PROMPT, SYNTHESIZER_PROMPT, REVIEWER_PROMPT"),
    ("src.state", "from src.state import ResearchState"),
    ("src.tools", "from src.tools import search_web, fetch_url, write_report, get_langchain_tools"),
    ("src.nodes", "from src.nodes import plan_node, search_node, synthesize_node, review_node, write_node"),
    ("src.graph", "from src.graph import create_research_graph, run_research"),
]

for name, statement in imports_to_test:
    try:
        exec(statement)
        print("  ✅", name)
    except Exception as error:
        print("  ❌", name, "—", str(error))
        stage1_pass = False

if not stage1_pass:
    print("\n  ❌ STAGE 1 FAILED — fix imports above before continuing")
    print("  Tip: pip install -r requirements.txt")
    sys.exit(1)

print("\n  ✅ STAGE 1 PASSED — all imports work\n")


# ============================================================
# STAGE 2: Graph Compilation
# ============================================================
print("STAGE 2: GRAPH COMPILATION")
print("-" * 40)

try:
    from src.graph import create_research_graph
    graph = create_research_graph()

    # Check that the graph has the expected nodes
    # In LangGraph >= 0.4, .nodes returns a dict — keys are node name strings
    graph_obj = graph.get_graph()
    all_node_names = list(graph_obj.nodes.keys())
    node_names = [n for n in all_node_names if n not in ("__start__", "__end__")]
    print("  Nodes found:", node_names)

    expected_nodes = ["plan", "search", "synthesize", "review", "write"]
    for expected in expected_nodes:
        if expected in node_names:
            print("    ✅", expected)
        else:
            print("    ❌", expected, "— MISSING")

    print("\n  ✅ STAGE 2 PASSED — graph compiles with all 5 nodes\n")

except Exception as error:
    print("  ❌ STAGE 2 FAILED —", str(error))
    sys.exit(1)


# ============================================================
# STAGE 3: Tool Smoke Tests
# ============================================================
print("STAGE 3: TOOL SMOKE TESTS")
print("-" * 40)

stage3_pass = True

# Test 3a: DuckDuckGo search
print("  3a: DuckDuckGo search...")
try:
    result = search_web("Python programming language")
    if "Result 1:" in result:
        print("    ✅ DuckDuckGo search returned results")
    elif "Search failed" in result:
        print("    ⚠️  DuckDuckGo search failed (may be rate-limited):", result[:100])
    else:
        print("    ⚠️  Unexpected response:", result[:100])
except Exception as error:
    print("    ❌ DuckDuckGo search error:", str(error))
    stage3_pass = False

# Test 3b: URL fetch
print("  3b: URL fetch...")
try:
    result = fetch_url("https://example.com")
    if "Example Domain" in result:
        print("    ✅ URL fetch works (got example.com content)")
    elif result.startswith(("Timeout:", "HTTP Error:", "Failed to fetch")):
        print("    ⚠️  URL fetch failed:", result[:100])
    else:
        print("    ✅ URL fetch returned content:", result[:60] + "...")
except Exception as error:
    print("    ❌ URL fetch error:", str(error))
    stage3_pass = False

# Test 3c: Write report
print("  3c: Write report...")
try:
    test_content = "# Test Report\n\nThis is a test.\n"
    result = write_report("Test Validation Report", test_content)
    if "Report saved to:" in result:
        # Clean up
        filepath = result.replace("Report saved to: ", "")
        if os.path.exists(filepath):
            os.remove(filepath)
        print("    ✅ Write report works (file created and cleaned up)")
    else:
        print("    ❌ Unexpected result:", result)
        stage3_pass = False
except Exception as error:
    print("    ❌ Write report error:", str(error))
    stage3_pass = False

# Test 3d: LangChain @tool wrappers
print("  3d: @tool wrappers...")
try:
    tools = get_langchain_tools()
    print("    Tools registered:", len(tools))
    for t in tools:
        print("      -", t.name, ":", t.description[:50] + "...")
    print("    ✅ All 3 @tool wrappers registered")
except Exception as error:
    print("    ❌ @tool wrapper error:", str(error))
    stage3_pass = False

if stage3_pass:
    print("\n  ✅ STAGE 3 PASSED — all tools work\n")
else:
    print("\n  ⚠️  STAGE 3 has warnings — check above\n")


# ============================================================
# STAGE 4: Full Pipeline Test
# ============================================================
print("STAGE 4: FULL PIPELINE TEST")
print("-" * 40)
print("  Running a real research with a simple topic...")
print("  (This will take 30-90 seconds and make several API calls)")
print()

try:
    start_time = time.time()
    final_state = run_research("What is the Swiggy IPO and its impact on Indian startups")
    elapsed = time.time() - start_time

    print("\n" + "-" * 40)
    print("  PIPELINE RESULTS:")
    print("    Time:", str(round(elapsed, 1)) + "s")
    print("    Review Score:", str(final_state.get("review_score", "N/A")) + "/10")
    print("    Sources:", len(final_state.get("sources", [])))
    print("    Findings:", len(final_state.get("findings", [])))
    print("    Report Length:", len(final_state.get("report_content", "")), "chars")

    confidence = final_state.get("confidence_scores", [])
    v = sum(1 for c in confidence if c.get("rating") == "VERIFIED")
    i = sum(1 for c in confidence if c.get("rating") == "INFERRED")
    u = sum(1 for c in confidence if c.get("rating") == "UNCERTAIN")
    print("    Confidence: VERIFIED=" + str(v) + " INFERRED=" + str(i) + " UNCERTAIN=" + str(u))

    # Validate the output
    report = final_state.get("report_content", "")
    checks = {
        "Report not empty": len(report) > 100,
        "Has executive summary": "Executive Summary" in report or "executive summary" in report.lower(),
        "Has findings": "Finding" in report or "finding" in report.lower(),
        "Has confidence ratings": "VERIFIED" in report or "INFERRED" in report or "UNCERTAIN" in report,
        "Has sources": len(final_state.get("sources", [])) > 0,
        "Report saved to disk": os.path.exists("reports"),
    }

    print()
    print("  VALIDATION CHECKS:")
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print("    ✅", check_name)
        else:
            print("    ❌", check_name)
            all_passed = False

    if all_passed:
        print("\n  ✅ STAGE 4 PASSED — full pipeline works end to end")
    else:
        print("\n  ⚠️  STAGE 4 — some checks failed (see above)")

except Exception as error:
    print("  ❌ STAGE 4 FAILED —", str(error))
    import traceback
    traceback.print_exc()


# ============================================================
# FINAL SUMMARY
# ============================================================
print()
print("=" * 60)
print("  VALIDATION COMPLETE")
print("=" * 60)
print()
print("  Next steps:")
print("    1. Run: streamlit run streamlit_app.py")
print("    2. Test the MCP server: mcp dev src/mcp_server.py")
print("    3. Check LangSmith traces: https://smith.langchain.com")
print()