import sys
from datetime import datetime
from pathlib import Path
from langgraph.graph import StateGraph, START, END
from brief import Brief, SAMPLE_NEWS
from analyst import analyze
from writer import write_report
from editor import edit, PASS_THRESHOLD

# The initial draft, plus up to 2 revisions, then we ship the best we have.
# This is the safety valve that stops the writer/editor looping forever.
MAX_DRAFTS = 3


def build_desk(demo: bool = False):
    """Build the pipeline. In demo mode the three agents are replaced with
    cached stand-ins, so the whole graph runs with no API key."""

    if demo:
        from demo import demo_analyze as run_analyst
        from demo import demo_write as run_writer
        from demo import demo_edit as run_editor
    else:
        run_analyst, run_writer, run_editor = analyze, write_report, edit

    # --- NODES: each wraps one agent and returns only the fields it changed ---

    def analyst_node(state: Brief) -> dict:
        print("  [analyst] researching...")
        return {"findings": run_analyst(state).findings}

    def writer_node(state: Brief) -> dict:
        n = state.revision_count + 1
        print(f"  [writer] {'drafting' if n == 1 else f'revising (draft {n})'}...")
        updated = run_writer(state)
        return {"draft": updated.draft, "revision_count": n}

    def editor_node(state: Brief) -> dict:
        updated = run_editor(state)
        print(f"  [editor] scored {updated.editor_score}/10")
        return {
            "editor_score": updated.editor_score,
            "editor_feedback": updated.editor_feedback,
        }

    # --- CONDITIONAL EDGE: ship, or send the draft back to the writer? ---

    def review_router(state: Brief) -> str:
        if state.editor_score >= PASS_THRESHOLD:
            print("  [router] passes the bar -> ship\n")
            return "ship"
        if state.revision_count >= MAX_DRAFTS:
            print("  [router] out of revisions -> ship best effort\n")
            return "ship"
        print(f"  [router] below {PASS_THRESHOLD} -> send back to writer\n")
        return "revise"

    # --- WIRE THE GRAPH ---

    g = StateGraph(Brief)
    g.add_node("analyst", analyst_node)
    g.add_node("writer", writer_node)
    g.add_node("editor", editor_node)

    g.add_edge(START, "analyst")
    g.add_edge("analyst", "writer")
    g.add_edge("writer", "editor")
    g.add_conditional_edges(
        "editor", review_router, {"ship": END, "revise": "writer"}
    )
    return g.compile()


def save_report(brief: Brief) -> Path:
    """Write the finished brief to reports/<timestamp>.md and return the path."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)          # make the folder if it's not there
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = reports_dir / f"{stamp}.md"
    path.write_text(brief.draft, encoding="utf-8")
    return path


if __name__ == "__main__":
    demo = "--demo" in sys.argv
    desk = build_desk(demo=demo)

    banner = "DEMO MODE (cached data, no API key needed)" if demo else "LIVE MODE"
    print(f"Running the rare-earth desk  [{banner}]\n")

    result = desk.invoke(Brief(**SAMPLE_NEWS))
    final = result if isinstance(result, Brief) else Brief(**result)

    print("=" * 70)
    print(f"FINAL  —  score {final.editor_score}/10  after {final.revision_count} draft(s)")
    print("=" * 70)
    print(final.draft)
    print("=" * 70)

    saved_to = save_report(final)
    print(f"\nSaved report to: {saved_to}")
    