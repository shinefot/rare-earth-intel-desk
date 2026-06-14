from anthropic import Anthropic
from dotenv import load_dotenv
from brief import Brief, SAMPLE_NEWS
from analyst import analyze

load_dotenv()
client = Anthropic()

# ---------------------------------------------------------------------------
# The Writer's instructions. Note this prompt defines the report STRUCTURE.
# Change this template and you change every report the desk ever produces.
# ---------------------------------------------------------------------------

WRITER_SYSTEM = """You are the lead writer for a rare-earth-elements intelligence desk \
read by venture capitalists. You turn an analyst's findings into one sharp, investable brief.

Ignore surface-level "supply chain crisis" framing. Focus on structural shifts: unlocked \
bottlenecks, non-dilutive funding (grants/loans), offtake agreements, regulatory inflection \
points, and technology that breaks the Chinese cost curve.

Write in this EXACT structure, in markdown:

# <PUNCHY HEADLINE>
*<one-line subtitle framing the investable angle>*

**Trigger:** <the news event in one sentence>

**What the surface reads as:** <the naive interpretation>

**What it actually is:** <the real significance, 2-3 sentences>

**Findings**
- *Geopolitical:* <synthesis of the geopolitical findings>
- *Technical:* <synthesis of the technical findings>
- *Pricing:* <synthesis of the pricing findings>

**The investable angle:** <2-4 sentences: where the real opportunity is and what to watch>

**Diligence flag:** <the single most important thing to verify before acting>

Be concrete and skeptical. Do not invent facts beyond the findings provided."""


def write_report(brief: Brief) -> Brief:
    """Turn the Brief's findings into a finished report draft.

    If the editor has already given feedback (i.e. this is a revision),
    fold that critique into the instructions so the rewrite addresses it.
    """
    revision_note = ""
    if brief.editor_feedback:
        revision_note = (
            f"\n\nThis is a REVISION. Your previous draft scored "
            f"{brief.editor_score}/10. The editor requires these changes:\n"
            f"{brief.editor_feedback}\n"
            f"Rewrite the brief to fully address this feedback."
        )

    user_msg = (
        f"News title: {brief.raw_title}\n\n"
        f"Original article:\n{brief.raw_text}\n\n"
        f"Analyst findings:\n{format_findings(brief.findings)}"
        f"{revision_note}\n\n"
        f"Write the brief."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=WRITER_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )

    brief.draft = "".join(b.text for b in response.content if b.type == "text")
    return brief


def format_findings(findings) -> str:
    """Lay the findings out as plain text for the Writer to read."""
    lines = []
    for f in findings:
        src = f" (source: {f.evidence_url})" if f.evidence_url else ""
        lines.append(f"- [{f.lens}, confidence {f.confidence}] {f.claim}{src}")
    return "\n".join(lines)


if __name__ == "__main__":
    brief = Brief(**SAMPLE_NEWS)

    print("Step 1/2: Analyst researching (web search, ~20-40s)...\n")
    brief = analyze(brief)
    print(f"  got {len(brief.findings)} findings.\n")

    print("Step 2/2: Writer drafting the brief...\n")
    brief = write_report(brief)

    print("=" * 70)
    print(brief.draft)
    print("=" * 70)
