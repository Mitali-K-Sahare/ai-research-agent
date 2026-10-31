"""
=============================================================================
Project 3: AI Research Agent
streamlit_app.py — Web UI (Enter a Topic, Watch the Agent Work)
=============================================================================

HOW TO RUN:
  streamlit run streamlit_app.py

WHAT IT DOES:
  - User enters a research topic
  - Shows real-time progress as each node runs
  - Displays the final report with confidence ratings
  - Download button for the markdown report

NOTE:
  This file is SEPARATE from the core engine (src/).
  The UI is thin — all intelligence lives in src/graph.py and src/nodes.py.
  Same separation pattern as Project 2.
=============================================================================
"""

# ── IMPORTS ─────────────────────────────────────────────────────────────────

# Streamlit is the web framework (same as Project 2)
import streamlit as st

# time is used for the elapsed time display
import time

# os is used to check if the reports folder exists
import os

# Import our research graph
from src.graph import create_research_graph
from src.config import REPORTS_DIR


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔍",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("🔍 AI Research Agent")
st.markdown(
    "Enter a topic and the agent will search the web, read sources, "
    "synthesize findings, and generate a structured research report "
    "with confidence-rated claims."
)
st.markdown("---")


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
# Streamlit reruns the entire script on every interaction.
# session_state persists data across reruns (same as Project 2).

if "research_complete" not in st.session_state:
    st.session_state.research_complete = False
    st.session_state.final_state = None
    st.session_state.elapsed_time = 0


# ============================================================
# TOPIC INPUT
# ============================================================

# Create two columns: input field + button
col_input, col_button = st.columns([4, 1])

with col_input:
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g., Impact of AI on software engineering jobs in India",
        label_visibility="collapsed",
    )

with col_button:
    run_button = st.button("🚀 Research", type="primary", use_container_width=True)


# ============================================================
# RUN RESEARCH
# ============================================================

if run_button and topic:
    # Reset state for a new research run
    st.session_state.research_complete = False
    st.session_state.final_state = None

    # Create the graph
    graph = create_research_graph()

    # Set up the initial state
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

    config = {"configurable": {"thread_id": "streamlit-research-001"}}

    # Show progress with a status container
    start_time = time.time()

    with st.status("🔬 Researching: " + topic, expanded=True) as status:

        st.write("📋 **Planning** — Generating search queries...")

        # We use stream_mode to get updates at each node
        # This lets us show progress as the agent works
        try:
            # invoke() runs the full graph and returns the final state
            # For Streamlit, we show a simple progress display
            final_state = graph.invoke(initial_state, config=config)

            elapsed = time.time() - start_time
            st.session_state.elapsed_time = round(elapsed, 1)
            st.session_state.final_state = final_state
            st.session_state.research_complete = True

            status.update(
                label="✅ Research complete! (" + str(round(elapsed, 1)) + "s)",
                state="complete",
            )

        except Exception as error:
            status.update(label="❌ Research failed", state="error")
            st.error("Error: " + str(error))


# ============================================================
# DISPLAY RESULTS
# ============================================================

if st.session_state.research_complete and st.session_state.final_state:
    final_state = st.session_state.final_state

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Quality Score", str(final_state["review_score"]) + "/10")
    with col2:
        st.metric("Sources Found", len(final_state["sources"]))
    with col3:
        st.metric("Findings", len(final_state["findings"]))
    with col4:
        st.metric("Time", str(st.session_state.elapsed_time) + "s")

    st.markdown("---")

    # Two-column layout: report + sidebar info
    col_report, col_info = st.columns([3, 1])

    with col_report:
        st.subheader("📄 Research Report")
        st.markdown(final_state["report_content"])

    with col_info:
        # Confidence summary
        st.subheader("📊 Confidence")
        confidence_scores = final_state.get("confidence_scores", [])

        verified_count = 0
        inferred_count = 0
        uncertain_count = 0

        for score in confidence_scores:
            rating = score.get("rating", "")
            if rating == "VERIFIED":
                verified_count = verified_count + 1
            elif rating == "INFERRED":
                inferred_count = inferred_count + 1
            elif rating == "UNCERTAIN":
                uncertain_count = uncertain_count + 1

        st.markdown("🟢 **Verified:** " + str(verified_count))
        st.markdown("🟡 **Inferred:** " + str(inferred_count))
        st.markdown("🔴 **Uncertain:** " + str(uncertain_count))

        # Review feedback
        st.subheader("📝 Review")
        feedback = final_state.get("review_feedback", "")
        if feedback:
            st.info(feedback)

        # Sources list
        st.subheader("🔗 Sources")
        sources = final_state.get("sources", [])
        for i in range(len(sources)):
            source = sources[i]
            title = source.get("title", "Untitled")
            url = source.get("url", "")
            st.markdown(str(i + 1) + ". [" + title + "](" + url + ")")

    # Download button
    st.markdown("---")
    st.download_button(
        label="📥 Download Report (.md)",
        data=final_state["report_content"],
        file_name="research_report.md",
        mime="text/markdown",
    )

elif run_button and not topic:
    st.warning("Please enter a research topic.")
