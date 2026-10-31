"""
=============================================================================
Project 3: AI Research Agent
nodes.py — The 5 Graph Nodes (The Agent's Brain)
=============================================================================

WHAT THIS FILE DOES:
  Defines the 5 node functions that make up the research workflow:
    1. plan_node       — Generate search queries from the topic
    2. search_node     — Execute one search query + fetch URL content
    3. synthesize_node — Combine all findings into a structured report
    4. review_node     — Score the report and identify gaps
    5. write_node      — Save the final report to a markdown file

HOW NODES WORK (Week 11 review):
  - Each node is a regular Python function
  - It receives the current state (a dictionary) as its only argument
  - It returns a dictionary with ONLY the fields it wants to update
  - LangGraph merges the updates into the state automatically

  Example:
    def my_node(state):
        # Read from state
        topic = state["topic"]
        # Do something
        result = process(topic)
        # Return ONLY the fields to update
        return {"processed_result": result}
=============================================================================
"""

# ── IMPORTS ─────────────────────────────────────────────────────────────────

# json is used to parse the LLM's JSON responses (plan_node, review_node)
import json

# HumanMessage and SystemMessage are LangChain's message types
# SystemMessage sets the LLM's role/persona
# HumanMessage is what we (the code) send to the LLM
# These are the same message types used since Week 5
from langchain_core.messages import HumanMessage, SystemMessage

# Import the LLM instance from our config file
# This is the single place where OpenAI/Groq is configured
from src.config import llm

# Import the prompts (all defined in one file for easy management)
from src.prompts import PLANNER_PROMPT, SYNTHESIZER_PROMPT, REVIEWER_PROMPT

# Import the core tool functions (not the @tool wrappers — we call them directly)
from src.tools import search_web, fetch_url, write_report

# Import settings we need for decisions
from src.config import MAX_SEARCH_QUERIES, MAX_CONTENT_LENGTH


# ============================================================
# NODE 1: PLAN — Generate Search Queries
# ============================================================
# INPUT:  state["topic"] — the research topic from the user
# OUTPUT: state["search_queries"] — list of search query strings
#         state["search_iteration"] — initialized to 0

def plan_node(state):
    """
    Takes the research topic and uses the LLM to generate
    specific search queries. This is the agent's "planning" step.
    """
    print("  [plan_node] Generating search queries...")

    topic = state["topic"]

    # Build the prompt by filling in the template variables
    # .format() replaces {topic} and {max_queries} with actual values
    filled_prompt = PLANNER_PROMPT.format(
        topic=topic,
        max_queries=MAX_SEARCH_QUERIES,
    )

    # Send to the LLM
    # SystemMessage tells the LLM what role to play
    # HumanMessage contains the actual instruction
    messages = [
        SystemMessage(content="You are a research planning assistant."),
        HumanMessage(content=filled_prompt),
    ]

    # llm.invoke() sends the messages and returns the LLM's response
    # response.content is the actual text the LLM generated
    response = llm.invoke(messages)
    raw_response = response.content

    # Parse the JSON response
    # The LLM should return something like: ["query 1", "query 2", "query 3"]
    # We wrap this in try/except because LLMs sometimes return imperfect JSON
    try:
        # Strip whitespace and any markdown code fences the LLM might add
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            # Remove ```json and ``` markers if present
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        search_queries = json.loads(cleaned)

        # Verify it's actually a list of strings
        if not isinstance(search_queries, list):
            search_queries = [str(search_queries)]

    except json.JSONDecodeError:
        # Fallback: if JSON parsing fails, create simple queries from the topic
        print("  [plan_node] WARNING: Could not parse LLM response as JSON")
        print("  [plan_node] Raw response:", raw_response[:200])
        search_queries = [
            topic,
            topic + " latest developments",
            topic + " analysis",
        ]

    print("  [plan_node] Generated", len(search_queries), "search queries")
    for i in range(len(search_queries)):
        print("    Query", str(i + 1) + ":", search_queries[i])

    # Return the state updates
    # search_queries uses Annotated[list, operator.add] so these APPEND
    # search_iteration starts at 0 (overwrite, not append)
    return {
        "search_queries": search_queries,
        "search_iteration": 0,
    }


# ============================================================
# NODE 2: SEARCH — Execute One Search Query + Fetch Content
# ============================================================
# INPUT:  state["search_queries"] — list of queries to execute
#         state["search_iteration"] — which query we're on (0-based index)
# OUTPUT: state["sources"] — search results (APPENDED via Annotated)
#         state["findings"] — extracted content (APPENDED via Annotated)
#         state["search_iteration"] — incremented by 1

def search_node(state):
    """
    Executes ONE search query (the current one based on search_iteration),
    fetches the top URLs, and extracts their content.
    This node runs multiple times — once per search query.
    """
    current_index = state["search_iteration"]
    queries = state["search_queries"]

    # Safety check: don't go beyond the available queries
    if current_index >= len(queries):
        print("  [search_node] No more queries to process")
        return {"search_iteration": current_index}

    query = queries[current_index]
    print("  [search_node] Searching query", str(current_index + 1) + "/" + str(len(queries)) + ":", query)

    # Step 1: Search the web
    search_results_text = search_web(query)

    # Step 2: Parse the search results to extract URLs
    # Our search_web function returns formatted text, so we need to
    # extract the URLs from lines that start with "  URL: "
    new_sources = []
    urls_to_fetch = []

    lines = search_results_text.split("\n")
    current_title = ""
    current_url = ""
    current_snippet = ""

    for line in lines:
        line = line.strip()
        if line.startswith("Title:"):
            current_title = line.replace("Title:", "").strip()
        elif line.startswith("URL:"):
            current_url = line.replace("URL:", "").strip()
        elif line.startswith("Snippet:"):
            current_snippet = line.replace("Snippet:", "").strip()

            # We have all 3 pieces — save this source
            if current_url and current_url != "No URL":
                source_info = {
                    "title": current_title,
                    "url": current_url,
                    "snippet": current_snippet,
                    "query": query,
                }
                new_sources.append(source_info)
                urls_to_fetch.append(current_url)

            # Reset for the next result
            current_title = ""
            current_url = ""
            current_snippet = ""

    print("  [search_node] Found", len(urls_to_fetch), "URLs to fetch")

    # Step 3: Fetch content from each URL
    new_findings = []
    for i in range(len(urls_to_fetch)):
        url = urls_to_fetch[i]
        print("    Fetching", str(i + 1) + "/" + str(len(urls_to_fetch)) + ":", url[:60] + "...")

        content = fetch_url(url)

        # Only keep results that actually have content
        # Skip error messages (they start with "Timeout:", "HTTP Error:", etc.)
        if not content.startswith(("Timeout:", "HTTP Error:", "Failed to fetch")):
            # Build a finding entry with source attribution
            finding = "SOURCE: " + url + "\n"
            finding = finding + "TITLE: " + new_sources[i]["title"] + "\n"
            finding = finding + "CONTENT:\n" + content
            new_findings.append(finding)
        else:
            print("    Skipped (error):", content[:100])

    print("  [search_node] Successfully extracted", len(new_findings), "findings")

    # Return updates — sources and findings APPEND (Annotated[list, operator.add])
    # search_iteration OVERWRITES (plain int)
    return {
        "sources": new_sources,
        "findings": new_findings,
        "search_iteration": current_index + 1,
    }


# ============================================================
# NODE 3: SYNTHESIZE — Combine Findings Into a Report
# ============================================================
# INPUT:  state["topic"], state["findings"], state["sources"]
# OUTPUT: state["report_content"] — the formatted research report
#         state["confidence_scores"] — list of confidence ratings

def synthesize_node(state):
    """
    Takes all gathered findings and uses the LLM to synthesize them
    into a structured research report with confidence ratings.
    """
    print("  [synthesize_node] Synthesizing", len(state["findings"]), "findings into a report...")

    topic = state["topic"]
    findings = state["findings"]

    # Build the sources text for the prompt
    # We concatenate all findings with separators
    sources_text = ""
    for i in range(len(findings)):
        sources_text = sources_text + "\n" + "=" * 40 + "\n"
        sources_text = sources_text + "FINDING " + str(i + 1) + ":\n"
        sources_text = sources_text + findings[i] + "\n"

    # Fill in the synthesizer prompt template
    filled_prompt = SYNTHESIZER_PROMPT.format(
        topic=topic,
        sources=sources_text,
    )

    # Send to the LLM
    messages = [
        SystemMessage(content="You are a research analyst."),
        HumanMessage(content=filled_prompt),
    ]

    response = llm.invoke(messages)
    report = response.content

    print("  [synthesize_node] Report generated:", len(report), "characters")

    # Extract confidence scores from the report
    # We look for lines containing "**Confidence:" and parse the rating
    confidence_scores = []
    report_lines = report.split("\n")
    for line in report_lines:
        if "**Confidence:" in line:
            if "VERIFIED" in line.upper():
                confidence_scores.append({"rating": "VERIFIED", "line": line.strip()})
            elif "INFERRED" in line.upper():
                confidence_scores.append({"rating": "INFERRED", "line": line.strip()})
            elif "UNCERTAIN" in line.upper():
                confidence_scores.append({"rating": "UNCERTAIN", "line": line.strip()})

    print("  [synthesize_node] Confidence ratings found:", len(confidence_scores))

    return {
        "report_content": report,
        "confidence_scores": confidence_scores,
    }


# ============================================================
# NODE 4: REVIEW — Score the Report and Identify Gaps
# ============================================================
# INPUT:  state["report_content"]
# OUTPUT: state["review_score"] — quality score 1-10
#         state["review_feedback"] — written feedback
#         state["search_queries"] — additional queries if score < 7 (APPENDED)

def review_node(state):
    """
    Evaluates the synthesized report's quality and either:
    - Accepts it (score >= 7) → proceeds to write
    - Rejects it (score < 7) → adds more search queries for another round
    """
    print("  [review_node] Reviewing report quality...")

    report = state["report_content"]

    # Fill in the reviewer prompt
    filled_prompt = REVIEWER_PROMPT.format(report=report)

    # Send to the LLM
    messages = [
        SystemMessage(content="You are a research quality reviewer."),
        HumanMessage(content=filled_prompt),
    ]

    response = llm.invoke(messages)
    raw_response = response.content

    # Parse the JSON response from the reviewer
    try:
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        review_data = json.loads(cleaned)

        score = int(review_data.get("score", 5))
        feedback = review_data.get("feedback", "No feedback provided")
        additional_queries = review_data.get("additional_queries", [])

    except (json.JSONDecodeError, ValueError):
        # If parsing fails, give a middle-of-the-road score
        print("  [review_node] WARNING: Could not parse review response")
        print("  [review_node] Raw response:", raw_response[:200])
        score = 6
        feedback = "Review parsing failed. Raw response: " + raw_response[:200]
        additional_queries = []

    print("  [review_node] Score:", str(score) + "/10")
    print("  [review_node] Feedback:", feedback[:100] + "...")

    # Build the return dictionary
    result = {
        "review_score": score,
        "review_feedback": feedback,
    }

    # If score is low, add more search queries
    # These APPEND to search_queries (Annotated[list, operator.add])
    # The conditional edge will route back to search_node
    if additional_queries:
        print("  [review_node] Adding", len(additional_queries), "additional queries")
        result["search_queries"] = additional_queries

    return result


# ============================================================
# NODE 5: WRITE — Save the Final Report
# ============================================================
# INPUT:  state["topic"], state["report_content"]
# OUTPUT: (saves file to disk, returns filepath info)

def write_node(state):
    """
    Saves the final research report as a markdown file.
    This is the last node in the workflow.
    """
    print("  [write_node] Saving report...")

    topic = state["topic"]
    report = state["report_content"]

    # Add metadata to the report
    # This adds a footer with the sources used and confidence summary
    sources = state.get("sources", [])
    review_score = state.get("review_score", 0)
    review_feedback = state.get("review_feedback", "")

    # Build a metadata footer
    footer = "\n\n---\n"
    footer = footer + "*Report generated by AI Research Agent*\n"
    footer = footer + "*Quality Score: " + str(review_score) + "/10*\n"
    footer = footer + "*Sources searched: " + str(len(sources)) + "*\n"

    full_report = report + footer

    # Save using our core write function
    result = write_report(topic, full_report)
    print("  [write_node]", result)

    return {
        "report_content": full_report,
    }
