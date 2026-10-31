"""
=============================================================================
Project 3: AI Research Agent
mcp_server.py — MCP Server (Tools Available to Any AI Client)
=============================================================================

WHAT THIS FILE DOES:
  Wraps our 3 research tools as an MCP (Model Context Protocol) server.
  Once running, ANY MCP client can discover and use these tools:
    - Claude Desktop
    - Cursor
    - VS Code Copilot
    - Any LangChain agent using langchain-mcp-adapters
    - Any custom MCP client

WEEK 12 REVIEW:
  MCP is like USB-C for AI tools:
    - Build the tool server ONCE using the MCP standard
    - ANY MCP client can discover and use your tools automatically
    - No need to rewrite tools for each AI platform

  Architecture:
    HOST (Claude, Cursor) ↔ CLIENT (connector) ↔ SERVER (this file)

HOW TO RUN:
  Test with MCP inspector:
    mcp dev src/mcp_server.py

  Or run directly:
    python src/mcp_server.py

HOW TO CONNECT:
  In Claude Desktop's config (claude_desktop_config.json):
    {
      "mcpServers": {
        "research-tools": {
          "command": "python",
          "args": ["src/mcp_server.py"]
        }
      }
    }
=============================================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── IMPORTS ─────────────────────────────────────────────────────────────────

# FastMCP is the high-level framework for building MCP servers
# It's included in the official MCP Python SDK (pip install "mcp[cli]")
# FastMCP does for MCP what FastAPI does for REST APIs:
#   - You write a Python function + add a decorator
#   - FastMCP handles all the protocol details (JSON-RPC, transport, etc.)
from mcp.server.fastmcp import FastMCP

# Import our CORE tool functions (not the @tool wrappers)
# These are the same functions used by our LangGraph workflow
# We're just exposing them through a different interface (MCP vs LangChain)
from src.tools import search_web, fetch_url, write_report


# ============================================================
# CREATE THE MCP SERVER
# ============================================================

# FastMCP("name") creates a new MCP server instance
# The name is how clients identify this server when they connect
# It's like naming a FastAPI app: app = FastAPI(title="My API")
mcp = FastMCP("ResearchToolsServer")


# ============================================================
# TOOL 1: WEB SEARCH
# ============================================================
# @mcp.tool() registers this function as an MCP tool
# This is similar to @tool in LangChain, but follows the MCP standard
# The docstring is what MCP clients show to the user/AI

@mcp.tool()
def web_search(query: str) -> str:
    """Search the web for information on any topic using DuckDuckGo.
    Returns titles, URLs, and snippets from the top search results.
    Free to use, no API key required."""

    # We call the SAME core function used by our LangGraph agent
    # One implementation, two interfaces — that's good engineering
    return search_web(query)


# ============================================================
# TOOL 2: FETCH URL CONTENT
# ============================================================

@mcp.tool()
def fetch_url_content(url: str) -> str:
    """Fetch and extract readable text content from a web page.
    Takes a URL and returns the main text, stripped of HTML tags.
    Useful for reading articles, blog posts, and documentation."""

    return fetch_url(url)


# ============================================================
# TOOL 3: WRITE MARKDOWN REPORT
# ============================================================

@mcp.tool()
def write_markdown_report(title: str, content: str) -> str:
    """Save a research report as a markdown file in the reports/ folder.
    Takes a title and content string, generates a timestamped filename,
    and writes the file. Returns the path where the file was saved."""

    return write_report(title, content)


# ============================================================
# RUN THE SERVER
# ============================================================
# When you run this file directly (python src/mcp_server.py),
# it starts the MCP server using stdio transport.
# stdio = communication happens through standard input/output
# This is the transport Claude Desktop and most MCP clients use.

if __name__ == "__main__":
    print("Starting Research Tools MCP Server...")
    print("Tools available: web_search, fetch_url_content, write_markdown_report")
    print("Connect with: mcp dev src/mcp_server.py")
    
