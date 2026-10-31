"""
=============================================================================
Project 3: AI Research Agent
run_research.py — Terminal Entry Point
=============================================================================

HOW TO RUN:
  python run_research.py

  It will ask you for a research topic, then run the full agent workflow:
    plan → search → synthesize → review → write

  The final report is saved as a .md file in the reports/ folder.
=============================================================================
"""

# ── IMPORTS ─────────────────────────────────────────────────────────────────

# sys.argv lets us optionally pass the topic as a command-line argument
# Example: python run_research.py "AI in Indian healthcare"
import sys

# Import the convenience function that runs the full research workflow
from src.graph import run_research


# ============================================================
# MAIN
# ============================================================

def main():
    """
    Get a research topic from the user (or command line) and run the agent.
    """
    print("\n" + "=" * 60)
    print("  AI RESEARCH AGENT — Terminal Mode")
    print("=" * 60)

    # Check if a topic was passed as a command-line argument
    # sys.argv[0] is the script name, sys.argv[1] would be the topic
    if len(sys.argv) > 1:
        # Join all arguments after the script name (handles multi-word topics)
        topic = " ".join(sys.argv[1:])
        print("  Topic (from command line):", topic)
    else:
        # Ask the user to type a topic
        print("  Enter a research topic (or press Enter for a demo topic):")
        topic = input("  > ").strip()

        # Default topic if the user just presses Enter
        if not topic:
            topic = "Impact of AI on software engineering jobs in India"
            print("  Using demo topic:", topic)

    # Run the full research workflow
    final_state = run_research(topic)

    # Display the report in the terminal
    print("\n" + "=" * 60)
    print("  GENERATED REPORT")
    print("=" * 60 + "\n")
    print(final_state["report_content"])

    # Show confidence summary
    confidence_scores = final_state.get("confidence_scores", [])
    if confidence_scores:
        print("\n" + "-" * 40)
        print("  CONFIDENCE SUMMARY")
        print("-" * 40)

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

        print("  VERIFIED:", verified_count)
        print("  INFERRED:", inferred_count)
        print("  UNCERTAIN:", uncertain_count)

    print("\n  Report saved to the reports/ folder.")
    print("  View it in any markdown viewer or text editor.")
    print("=" * 60 + "\n")


# ── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
