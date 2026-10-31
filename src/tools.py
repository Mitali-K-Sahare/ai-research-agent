"""
=============================================================================
Project 3: AI Research Agent
tools.py — The 3 Research Tools
=============================================================================

WHAT THIS FILE DOES:
  Defines 3 tools the research agent needs:
    1. web_search     — Search the internet using DuckDuckGo (free, no API key)
    2. fetch_url_content — Fetch and extract readable text from a URL
    3. write_markdown_report — Save a research report as a .md file

ARCHITECTURE:
  Each tool has TWO versions:
    - A CORE FUNCTION (plain Python) — does the actual work
    - A @tool WRAPPER (LangChain) — makes it usable by LangChain agents

  The core functions are also imported by mcp_server.py to create MCP tools.
  This way we write the logic ONCE and expose it TWO ways:
    - LangChain @tool  → used by our LangGraph workflow
    - MCP @mcp.tool()  → usable by Claude Desktop, Cursor, any MCP client

WEEK 10 REVIEW:
  @tool is a decorator from langchain_core.tools.
  It tells LangChain: "the LLM is allowed to call this function."
  The docstring becomes the tool DESCRIPTION — the LLM reads it to decide
  WHEN to use this tool. Good description = good tool selection.
=============================================================================
"""

# ── IMPORTS ─────────────────────────────────────────────────────────────────

# os is used for file path operations (creating directories, joining paths)
import os

# datetime gives us timestamps for report filenames
from datetime import datetime

# re (regular expressions) is used to clean filenames
# We remove special characters that would break file paths
import re

# requests is Python's standard library for making HTTP calls
# We use it to fetch web page content from URLs
import requests

# BeautifulSoup extracts readable text from HTML
# Without it, we'd get raw HTML tags mixed with the actual content
from bs4 import BeautifulSoup

# DDGS is the DuckDuckGo Search class
# It lets us search the web programmatically — free, no API key needed
# Week 10 used this same class for the search tool
from ddgs import DDGS

# @tool decorator from LangChain (Week 10 review)
# Turns a regular Python function into a "tool" the LLM can call
from langchain_core.tools import tool

# Import settings from our config file
from src.config import MAX_CONTENT_LENGTH, SEARCH_RESULTS_PER_QUERY, REPORTS_DIR


# ============================================================
# CORE FUNCTION 1: WEB SEARCH
# ============================================================
# This is the actual implementation. No decorators.
# Both the @tool wrapper and the MCP server use this function.

def search_web(query: str) -> str:
    """
    Search the web using DuckDuckGo and return formatted results.

    Args:
        query: The search query string (e.g., "AI trends India 2025")

    Returns:
        A formatted string with titles, URLs, and snippets from search results.
        Returns an error message if the search fails.
    """
    try:
        # DDGS() creates a DuckDuckGo search client
        # .text() performs a text search and returns a list of result dictionaries
        # max_results limits how many results we get back
        searcher = DDGS()
        raw_results = searcher.text(query, max_results=SEARCH_RESULTS_PER_QUERY)

        # If no results came back, tell the caller
        if not raw_results:
            return "No search results found for: " + query

        # Format each result into a readable string
        # Each result dict has: "title", "href" (URL), "body" (snippet)
        formatted_results = []
        for i in range(len(raw_results)):
            result = raw_results[i]
            title = result.get("title", "No title")
            url = result.get("href", "No URL")
            snippet = result.get("body", "No description")

            # Build a clean, numbered entry
            entry = "Result " + str(i + 1) + ":\n"
            entry = entry + "  Title: " + title + "\n"
            entry = entry + "  URL: " + url + "\n"
            entry = entry + "  Snippet: " + snippet
            formatted_results.append(entry)

        # Join all results with blank lines between them
        output = "\n\n".join(formatted_results)
        return output

    except Exception as error:
        # If DuckDuckGo is down or rate-limited, return a clear error
        # NEVER let a tool crash — always return a string the agent can work with
        return "Search failed for '" + query + "': " + str(error)


# ============================================================
# CORE FUNCTION 2: FETCH URL CONTENT
# ============================================================

def fetch_url(url: str) -> str:
    """
    Fetch a web page and extract its readable text content.

    Args:
        url: The full URL to fetch (e.g., "https://example.com/article")

    Returns:
        The extracted text content (truncated to MAX_CONTENT_LENGTH characters).
        Returns an error message if the fetch fails.
    """
    try:
        # requests.get() makes an HTTP GET request to the URL
        # timeout=10 means: give up if the server doesn't respond in 10 seconds
        # headers with User-Agent: some websites block requests without this
        headers = {"User-Agent": "Mozilla/5.0 (Research Agent)"}
        response = requests.get(url, timeout=10, headers=headers)

        # raise_for_status() throws an error if the HTTP status code is 4xx or 5xx
        # For example: 404 (page not found), 500 (server error)
        response.raise_for_status()

        # Parse the HTML using BeautifulSoup
        # "html.parser" is Python's built-in HTML parser (no extra install needed)
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove <script> and <style> tags — they contain code, not readable text
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # get_text() extracts all visible text from the HTML
        # separator=" " puts spaces between elements (instead of jamming them together)
        # strip=True removes leading/trailing whitespace from each piece
        raw_text = soup.get_text(separator=" ", strip=True)

        # Truncate to MAX_CONTENT_LENGTH characters
        # Web pages can be 50,000+ characters — we only need the first chunk
        if len(raw_text) > MAX_CONTENT_LENGTH:
            truncated_text = raw_text[:MAX_CONTENT_LENGTH] + "... [truncated]"
        else:
            truncated_text = raw_text

        return truncated_text

    except requests.exceptions.Timeout:
        return "Timeout: " + url + " took too long to respond"

    except requests.exceptions.HTTPError as error:
        return "HTTP Error for " + url + ": " + str(error)

    except Exception as error:
        # Catch-all for any other errors (DNS failure, SSL error, etc.)
        return "Failed to fetch " + url + ": " + str(error)


# ============================================================
# CORE FUNCTION 3: WRITE MARKDOWN REPORT
# ============================================================

def write_report(title: str, content: str) -> str:
    """
    Save a research report as a markdown (.md) file.

    Args:
        title:   The report title (used to generate the filename)
        content: The full report content in markdown format

    Returns:
        The filepath where the report was saved, or an error message.
    """
    try:
        # Create the reports/ directory if it doesn't exist
        # os.makedirs with exist_ok=True won't crash if the folder already exists
        os.makedirs(REPORTS_DIR, exist_ok=True)

        # Clean the title to make a safe filename
        # re.sub replaces any character that ISN'T a letter, number, or space with ""
        # Then we replace spaces with underscores and convert to lowercase
        clean_title = re.sub(r"[^a-zA-Z0-9 ]", "", title)
        clean_title = clean_title.replace(" ", "_").lower()

        # Add a timestamp so we never overwrite previous reports
        # strftime formats the current date/time as "20250627_143022"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Build the full filename: "reports/ai_in_healthcare_20250627_143022.md"
        filename = clean_title + "_" + timestamp + ".md"
        filepath = os.path.join(REPORTS_DIR, filename)

        # Write the content to the file
        # encoding="utf-8" handles special characters (like em dashes, accents)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)

        return "Report saved to: " + filepath

    except Exception as error:
        return "Failed to save report: " + str(error)


# ============================================================
# LANGCHAIN @tool WRAPPERS
# ============================================================
# These wrap the core functions with the @tool decorator.
# The docstring is CRITICAL — it's what the LLM reads to decide
# which tool to use. (Week 10 lesson: good descriptions = good tool use)

@tool
def web_search(query: str) -> str:
    """Search the web for information on a topic using DuckDuckGo.
    Returns titles, URLs, and snippets from top search results.
    Use this when you need to find current information on any topic."""
    return search_web(query)


@tool
def fetch_url_content(url: str) -> str:
    """Fetch the full text content from a web page URL.
    Returns the readable text extracted from the page.
    Use this after web_search to read the full content of promising results."""
    return fetch_url(url)


@tool
def write_markdown_report(title: str, content: str) -> str:
    """Save a research report as a markdown file in the reports/ folder.
    Returns the filepath where the report was saved.
    Use this when the research is complete and the report is ready to save."""
    return write_report(title, content)


# ============================================================
# CONVENIENCE: Get all tools as a list
# ============================================================
# This is useful when binding tools to an LLM or registering them
# with an agent. Instead of listing them manually everywhere,
# call get_langchain_tools() and get the complete list.

def get_langchain_tools():
    """Return a list of all LangChain @tool functions."""
    return [web_search, fetch_url_content, write_markdown_report]


# ============================================================
# TEST: Run this file directly to verify tools work
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Testing Research Tools")
    print("=" * 60)

    # Test 1: Web Search
    print("\n--- Test 1: Web Search ---")
    search_result = search_web("artificial intelligence trends India 2025")
    # Print only the first 500 characters to keep output manageable
    print(search_result[:500])

    # Test 2: Fetch URL Content
    print("\n--- Test 2: Fetch URL Content ---")
    fetch_result = fetch_url("https://example.com")
    print(fetch_result[:300])

    # Test 3: Write Report
    print("\n--- Test 3: Write Markdown Report ---")
    test_content = "# Test Report\n\nThis is a test report.\n"
    write_result = write_report("Test Report", test_content)
    print(write_result)

    print("\n" + "=" * 60)
    print("  All tools tested successfully!")
    print("=" * 60)
