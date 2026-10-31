"""
=============================================================================
Project 3: AI Research Agent
graph.py — The LangGraph Workflow (Putting It All Together)
=============================================================================

WHAT THIS FILE DOES:
  Assembles the 5 nodes into a LangGraph StateGraph with conditional edges.
  This is where the WORKFLOW is defined — the order of operations and the
  decision points that control the agent's behavior.

THE WORKFLOW:
  START → plan_node → search_node ⟲ (loop) → synthesize_node
       → review_node → (accept/revise) → write_node → END

  Two conditional edges:
    1. should_continue_searching: after search, loop or move to synthesize?
    2. should_revise: after review, accept (→ write) or revise (→ search more)?

WEEK 11 REVIEW:
  - StateGraph(MyState) creates a graph with typed state
  - add_node("name", function) registers a node
  - add_edge(A, B) connects A → B (always)
  - add_conditional_edges(A, func, {result: next_node}) adds a decision point
  - START and END are special nodes marking the graph's boundaries
  - compile() freezes the graph so it can be executed
  - MemorySaver() enables checkpointing (resume after crashes)
=============================================================================
"""

# ── IMPORTS ─────────────────────────────────────────────────────────────────

# StateGraph is the main LangGraph class for building workflows
# START and END are special constants marking graph boundaries
from langgraph.graph import StateGraph, START, END

# MemorySaver saves graph state at each step
# If the agent crashes mid-run, you can resume from the last checkpoint
# Week 11 introduced this as "checkpointing"
from langgraph.checkpoint.memory import MemorySaver

# Import our state definition
from src.state import ResearchState

# Import all 5 node functions
from src.nodes import plan_node, search_node, synthesize_node, review_node, write_node

# Import settings for decision thresholds
from src.config import MIN_REVIEW_SCORE, MAX_SEARCH_ITERATIONS


# ============================================================
# CONDITIONAL EDGE 1: Should we keep searching?
# ============================================================
# Called AFTER search_node runs
# Decides: run search_node again (more queries) or move to synthesize?

def should_continue_searching(state):
    """
    Check if there are more search queries to process.

    Returns:
        "search_more" — if there are unprocessed queries left
        "synthesize"  — if all queries have been processed
    """
    current_iteration = state["search_iteration"]
    total_queries = len(state["search_queries"])

    if current_iteration < total_queries:
        print("  [router] More queries to process ("
              + str(current_iteration) + "/" + str(total_queries)
              + ") → searching more")
        return "search_more"
    else:
        print("  [router] All queries processed → synthesizing")
        return "synthesize"


# ============================================================
# CONDITIONAL EDGE 2: Should we revise?
# ============================================================
# Called AFTER review_node runs
# Decides: accept the report (→ write) or search more (→ search again)?

def should_revise(state):
    """
    Check if the report quality is good enough.

    Returns:
        "accept"    — if score >= MIN_REVIEW_SCORE or we've hit max iterations
        "revise"    — if score < MIN_REVIEW_SCORE and we can still search more
    """
    score = state["review_score"]
    iteration = state["search_iteration"]

    # Accept if: score is good enough OR we've hit the iteration limit
    if score >= MIN_REVIEW_SCORE:
        print("  [router] Score", str(score) + "/10 >= " + str(MIN_REVIEW_SCORE) + " → accepting report")
        return "accept"

    if iteration >= MAX_SEARCH_ITERATIONS:
        print("  [router] Hit max iterations (" + str(MAX_SEARCH_ITERATIONS)
              + ") → accepting report despite score " + str(score))
        return "accept"

    # Score is low AND we can still search → revise
    print("  [router] Score", str(score) + "/10 < " + str(MIN_REVIEW_SCORE)
          + " → searching for more sources")
    return "revise"


# ============================================================
# BUILD THE GRAPH
# ============================================================

def create_research_graph():
    """
    Assemble the complete research workflow as a LangGraph StateGraph.

    Returns:
        A compiled graph ready to be invoked with .invoke()
    """

    # Step 1: Create the graph with our state type
    # StateGraph(ResearchState) tells LangGraph what shape the state should have
    graph_builder = StateGraph(ResearchState)

    # Step 2: Register all 5 nodes
    # add_node("name", function) — the name is used in edges to reference the node
    graph_builder.add_node("plan", plan_node)
    graph_builder.add_node("search", search_node)
    graph_builder.add_node("synthesize", synthesize_node)
    graph_builder.add_node("review", review_node)
    graph_builder.add_node("write", write_node)

    # Step 3: Connect the nodes with edges

    # START → plan (always start with planning)
    graph_builder.add_edge(START, "plan")

    # plan → search (after planning, start searching)
    graph_builder.add_edge("plan", "search")

    # search → CONDITIONAL: search more or synthesize?
    # should_continue_searching returns "search_more" or "synthesize"
    # The dict maps each return value to the next node
    graph_builder.add_conditional_edges(
        "search",                        # after this node...
        should_continue_searching,        # call this function...
        {                                 # and route based on its return value:
            "search_more": "search",      #   "search_more" → loop back to search
            "synthesize": "synthesize",   #   "synthesize"  → move to synthesize
        }
    )

    # synthesize → review (always review after synthesizing)
    graph_builder.add_edge("synthesize", "review")

    # review → CONDITIONAL: accept or revise?
    # should_revise returns "accept" or "revise"
    graph_builder.add_conditional_edges(
        "review",                    # after this node...
        should_revise,               # call this function...
        {                            # and route based on its return value:
            "accept": "write",       #   "accept" → save the report
            "revise": "search",      #   "revise" → go back to searching
        }
    )

    # write → END (report is saved, we're done)
    graph_builder.add_edge("write", END)

    # Step 4: Compile with checkpointing
    # MemorySaver stores state at each node — enables resume after crashes
    checkpointer = MemorySaver()
    graph = graph_builder.compile(checkpointer=checkpointer)

    print("  Research graph compiled successfully!")
    return graph


# ============================================================
# CONVENIENCE: Run a research task
# ============================================================

def run_research(topic: str) -> dict:
    """
    Run a complete research task from start to finish.

    Args:
        topic: The research topic (e.g., "AI in Indian healthcare")

    Returns:
        The final state dictionary with the complete report and metadata.
    """
    print("\n" + "=" * 60)
    print("  AI RESEARCH AGENT")
    print("  Topic:", topic)
    print("=" * 60 + "\n")

    # Build the graph
    graph = create_research_graph()

    # Set up the initial state
    # Only "topic" is required — everything else starts empty
    initial_state = {
        "topic": topic,
        "search_queries": [],
        "sources": [],
        "findings": [],
        "report_content": "",
        "confidence_scores": [],
        "review_score": 0,
        "review_feedback": "",
        "search_iteration": 0,
    }

    # LangGraph requires a thread_id for checkpointing
    # This identifies this particular run
    config = {"configurable": {"thread_id": "research-001"}}

    # invoke() runs the graph from START to END
    # It follows all edges and conditional edges automatically
    print("Starting research...\n")
    final_state = graph.invoke(initial_state, config=config)

    print("\n" + "=" * 60)
    print("  RESEARCH COMPLETE")
    print("  Review Score:", str(final_state["review_score"]) + "/10")
    print("  Sources Found:", len(final_state["sources"]))
    print("  Findings Extracted:", len(final_state["findings"]))
    print("=" * 60)

    return final_state


# ============================================================
# GRAPH VISUALIZATION
# ============================================================

def save_graph_image(filepath: str = "research_agent_graph.png"):
    """
    Save a visual diagram of the graph workflow as a PNG image.
    Uses LangGraph's built-in Mermaid diagram generator.
    """
    try:
        graph = create_research_graph()
        # draw_mermaid_png() generates a PNG image of the graph
        # This shows all nodes and edges visually
        png_data = graph.get_graph().draw_mermaid_png()

        with open(filepath, "wb") as file:
            file.write(png_data)

        print("Graph diagram saved to:", filepath)
    except Exception as error:
        print("Could not generate graph image:", str(error))
        print("This is optional — it requires the 'mermaid' library.")
