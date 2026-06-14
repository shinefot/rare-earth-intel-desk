import json
from anthropic import Anthropic
from dotenv import load_dotenv
from brief import Brief, Finding, SAMPLE_NEWS

load_dotenv()
client = Anthropic()

# ---------------------------------------------------------------------------
# The Analyst's instructions. This system prompt is what turns a general
# chatbot into a specialist that thinks like a rare-earth VC analyst AND
# returns its work in a fixed, machine-readable shape.
# ---------------------------------------------------------------------------

ANALYST_SYSTEM = """You are a rare-earth-elements intelligence analyst writing for a \
venture-capital audience. You evaluate every news item through exactly three lenses:

- geopolitical: export controls, quotas, government funding, supply-chain decoupling
- technical: feasibility, scale (bench vs pilot vs commercial), CapEx / process impact
- pricing: spot-price dynamics, cost-curve position, ability to survive predatory pricing

Use the web_search tool to verify the article's claims and add current context \
(recent policy moves, comparable companies, price action). Be skeptical: separate \
demonstrated facts from company marketing.

Produce between 3 and 6 findings, spread across the lenses. Each finding must have:
- "lens": one of "geopolitical", "technical", "pricing"
- "claim": one or two sharp sentences stating the INSIGHT (not a summary of the article)
- "evidence_url": a source URL if the point rests on something you found via search, else null
- "confidence": one of "low", "medium", "high"

Return ONLY a JSON array of these findings as your final message. \
No preamble, no explanation, no markdown code fences."""


def analyze(brief: Brief) -> Brief:
    """Run the Analyst on a Brief and fill in its findings."""
    user_msg = f"Title: {brief.raw_title}\n\nArticle:\n{brief.raw_text}"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=ANALYST_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
    )

    # The reply can contain several blocks (search calls, results, text).
    # We want only the text the model wrote, joined together.
    text = "".join(
        block.text for block in response.content if block.type == "text"
    )

    brief.findings = parse_findings(text)
    return brief


def parse_findings(text: str) -> list[Finding]:
    """Pull the JSON array out of the model's reply and validate each item."""
    cleaned = extract_json_array(text)
    raw_items = json.loads(cleaned)          # text -> Python list of dicts
    return [Finding(**item) for item in raw_items]   # dicts -> validated Findings


def extract_json_array(text: str) -> str:
    """Defensive: isolate the [ ... ] array even if the model adds stray text."""
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON array found in model reply:\n{text}")
    return text[start : end + 1]


if __name__ == "__main__":
    brief = Brief(**SAMPLE_NEWS)
    print("Analyzing (the model is searching the web — this can take 20-40s)...\n")

    try:
        brief = analyze(brief)
    except Exception as e:
        print("Something went wrong turning the reply into findings:")
        print(e)
        raise

    print(f"Got {len(brief.findings)} findings:\n")
    for f in brief.findings:
        print(f"[{f.lens.upper()} | confidence: {f.confidence}]")
        print(f"  {f.claim}")
        if f.evidence_url:
            print(f"  source: {f.evidence_url}")
        print()
        