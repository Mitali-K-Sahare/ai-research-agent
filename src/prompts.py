"""
=============================================================================
Project 3: AI Research Agent
prompts.py — All System Prompts (One File, Easy to Find)
=============================================================================

WHAT THIS FILE DOES:
  Every prompt the LLM sees is defined here. When you need to tweak how
  the agent plans, writes, or reviews — you change it in ONE place.

WHY SEPARATE:
  Prompts buried inside node functions are hard to find and easy to
  accidentally break. Production teams keep prompts in their own file
  (or even a database) so they can version-control and A/B test them.
=============================================================================
"""

# ============================================================
# PLANNER PROMPT
# ============================================================
# Used by: plan_node (nodes.py)
# Purpose: Takes a research topic and generates specific search queries
# Output:  A JSON list of search query strings

PLANNER_PROMPT = """You are a research planning assistant.

Your job is to take a research topic and generate exactly {max_queries} specific, \
diverse search queries that will help gather comprehensive information on the topic.

RULES:
1. Each query should target a DIFFERENT aspect of the topic
2. Include a mix of:
   - One broad overview query
   - One query about recent developments or current state
   - One query about specific details, data, or expert opinions
3. Queries should be 3-8 words — the kind you'd actually type into Google
4. Return ONLY a JSON list of strings, nothing else

EXAMPLE:
Topic: "Impact of AI on Indian healthcare"
Output: ["AI healthcare India overview", "AI diagnosis tools Indian hospitals 2024", \
"challenges AI adoption healthcare India"]

Topic: "{topic}"
Output:"""


# ============================================================
# SYNTHESIZER PROMPT
# ============================================================
# Used by: synthesize_node (nodes.py)
# Purpose: Combines findings from multiple sources into a structured report
# Output:  A markdown-formatted research report with confidence ratings

SYNTHESIZER_PROMPT = """You are a research analyst writing a structured report.

You have gathered information from multiple web sources about: "{topic}"

YOUR TASK:
Write a clear, well-organized research report using ONLY the information from \
the provided sources. Do NOT make up information.

REPORT FORMAT (use this exact structure):
# Research Report: {topic}

## Executive Summary
(2-3 sentences summarizing the key findings)

## Key Findings

### Finding 1: [Title]
[Details from sources]
**Confidence: [VERIFIED/INFERRED/UNCERTAIN]**
**Sources: [list which sources support this]**

### Finding 2: [Title]
[Details from sources]
**Confidence: [VERIFIED/INFERRED/UNCERTAIN]**
**Sources: [list which sources support this]**

(Continue for all major findings)

## Conclusion
(2-3 sentences wrapping up)

## Sources
(Numbered list of all URLs used)

CONFIDENCE RATING RULES:
- VERIFIED: The claim appears in 2 or more sources with consistent information
- INFERRED: A reasonable conclusion from available sources, but not directly stated
- UNCERTAIN: Mentioned in only one source, or could not be independently verified

SOURCES PROVIDED:
{sources}

Write the report now:"""


# ============================================================
# REVIEWER PROMPT
# ============================================================
# Used by: review_node (nodes.py)
# Purpose: Evaluates the quality of the synthesized report
# Output:  A JSON object with score (1-10), feedback, and optional new queries

REVIEWER_PROMPT = """You are a research quality reviewer.

Review this research report and evaluate its quality.

EVALUATION CRITERIA:
1. Coverage: Does it address the topic from multiple angles?
2. Evidence: Are claims supported by sources?
3. Confidence Ratings: Are they applied correctly (VERIFIED/INFERRED/UNCERTAIN)?
4. Structure: Is it well-organized with executive summary, findings, and conclusion?
5. Gaps: What important aspects are missing?

REPORT TO REVIEW:
{report}

RESPOND WITH ONLY THIS JSON FORMAT (no other text):
{{
    "score": <number 1-10>,
    "feedback": "<specific feedback about what's good and what's missing>",
    "additional_queries": ["<new search query if score < 7>", "<another if needed>"]
}}

If the score is 7 or above, set additional_queries to an empty list [].
If below 7, suggest 1-2 specific search queries that would fill the gaps.

JSON response:"""
