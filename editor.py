import json
from anthropic import Anthropic
from dotenv import load_dotenv
from brief import Brief

load_dotenv()
client = Anthropic()

# How good a draft must be to ship. Below this, it goes back to the Writer.
PASS_THRESHOLD = 8

# ---------------------------------------------------------------------------
# The Editor's instructions: a rubric, a numeric score, and actionable feedback.
# This is the quality bar of the whole desk, written in plain English.
# ---------------------------------------------------------------------------

EDITOR_SYSTEM = """You are a demanding managing editor for a rare-earth-elements \
venture-capital intelligence desk. You score a draft brief against a rubric and decide \
whether it ships.

Score the draft from 0 to 10, judging:
- Clear, SPECIFIC investable angle (not generic "supply chain crisis" talk)
- Skeptical: separates demonstrated fact from company marketing
- Grounded in the findings; invents no facts
- Sharp VC voice; follows the required structure
- Names concrete mechanisms (funding programs, offtakes, cost drivers) where relevant

Be strict. A high score is earned, not given.

Return ONLY a JSON object — no preamble, no markdown fences:
{"score": <integer 0-10>, "feedback": "<specific, actionable critique the writer can \
act on. If the draft is excellent, say precisely what works.>"}"""


def edit(brief: Brief) -> Brief:
    """Score the Brief's current draft and record the score + feedback."""
    user_msg = f"Evaluate this draft brief:\n\n{brief.draft}"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=EDITOR_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )

    text = "".join(b.text for b in response.content if b.type == "text")
    result = parse_evaluation(text)

    brief.editor_score = result["score"]
    brief.editor_feedback = result["feedback"]
    return brief


def parse_evaluation(text: str) -> dict:
    """Pull the {score, feedback} object out of the model's reply."""
    cleaned = extract_json_object(text)
    return json.loads(cleaned)


def extract_json_object(text: str) -> str:
    """Defensive: isolate the { ... } object even if the model adds stray text."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in model reply:\n{text}")
    return text[start : end + 1]


if __name__ == "__main__":
    from brief import SAMPLE_NEWS
    from analyst import analyze
    from writer import write_report

    brief = Brief(**SAMPLE_NEWS)

    print("Analyst researching (web search, ~20-40s)...")
    brief = analyze(brief)
    print("Writer drafting...")
    brief = write_report(brief)
    print("Editor evaluating...\n")
    brief = edit(brief)

    verdict = "SHIPS" if brief.editor_score >= PASS_THRESHOLD else "NEEDS REVISION"
    print("=" * 70)
    print(f"SCORE: {brief.editor_score}/10   ->   {verdict}")
    print(f"\nEDITOR FEEDBACK:\n{brief.editor_feedback}")
    print("=" * 70)
    