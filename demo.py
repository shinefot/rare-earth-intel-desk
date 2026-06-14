"""
Offline demo data + stand-in agents.

These functions mimic the real Analyst / Writer / Editor but return CACHED
results instead of calling the model, so the project runs with no API key.
The graph, the router, and the revision loop all still run for real — only
the three LLM calls are replaced. The cached run is scripted so the editor
rejects the first draft and accepts the second, showing the loop in action.
"""

import time
from brief import Brief, Finding

# A small pause so the printed trace reads like a live run (purely cosmetic).
STEP_PAUSE = 0.6


# --- Cached Analyst output -------------------------------------------------

CACHED_FINDINGS = [
    {
        "lens": "geopolitical",
        "claim": "The announcement lands amid the post-2025 Chinese heavy-REE "
                 "licensing regime, so any credible non-Chinese dysprosium source "
                 "has a structural buyer base — but government capital flows to "
                 "pilot-scale or beyond, not bench-scale startups.",
        "evidence_url": "https://example.com/china-ree-controls",
        "confidence": "high",
    },
    {
        "lens": "technical",
        "claim": "A 99% purity claim at bench scale with no disclosed throughput "
                 "is a chemistry result, not an engineering one; the open question "
                 "is grams-per-hour, not percent-pure.",
        "evidence_url": None,
        "confidence": "high",
    },
    {
        "lens": "pricing",
        "claim": "Even a real cost advantage only matters if it survives Chinese "
                 "oxide price cuts; dysprosium's recent drawdown shows incumbents "
                 "can compress margins faster than a pilot plant can scale.",
        "evidence_url": "https://example.com/dy-price-drawdown",
        "confidence": "medium",
    },
]


# --- Two cached Writer drafts (v1 weak, v2 strong) -------------------------

DRAFT_V1 = """# A Domestic Rare Earth Breakthrough

*Helix Minerals may have cracked heavy rare earth separation*

**Trigger:** Helix Minerals announced 99% pure dysprosium from a new bio-separation process.

**What the surface reads as:** A promising step for U.S. rare earth independence.

**What it actually is:** A potentially important development given how much rare earths
matter to the supply chain and national security.

**Findings**
- *Geopolitical:* Rare earths are strategically important and China dominates supply.
- *Technical:* The process sounds innovative and could reduce costs.
- *Pricing:* Lower costs would help compete with China.

**The investable angle:** Rare earth processing is a critical space and worth watching
as the U.S. tries to build domestic capacity.

**Diligence flag:** Confirm the technology actually works.
"""

DRAFT_V2 = """# Bio-Bugs Won't Save the Dysprosium Supply Chain

*Helix Minerals' bench-scale purity claim is scientifically plausible — and
strategically irrelevant for the next five years*

**Trigger:** Helix Minerals announced 99%-pure dysprosium oxide at lab scale via an
engineered-microbe bio-separation process that skips conventional solvent extraction.

**What the surface reads as:** A domestic breakthrough that undercuts China's cost curve
on heavy rare earths at exactly the right geopolitical moment.

**What it actually is:** A chemistry milestone wearing an engineering costume. Purity is
the easy number; the bench-scale-only result with no throughput disclosed means this is
years from the pilot scale where government capital and offtakes actually flow.

**Findings**
- *Geopolitical:* Under the post-2025 Chinese licensing regime every non-Chinese gram has
  a structural buyer — but DOE/DoD money targets pilot-stage projects, not lab benches.
- *Technical:* 99% purity with no grams-per-hour figure is a result, not a plant. The
  question that decides this company is throughput, not percent-pure.
- *Pricing:* A cost edge only matters if it survives Chinese oxide price cuts; the recent
  dysprosium drawdown shows incumbents can compress margins faster than a pilot can scale.

**The investable angle:** Don't bet on the microbes — track the funding architecture.
The real signal is whether Helix files for a DOE Title XVII-style loan or lands an offtake;
that's the moment the market validates pilot-readiness. Until then it's a science project.

**Diligence flag:** Demand a demonstrated throughput figure (kg/hr) at pilot scale and
proof the bio-process distinguishes *separation* from mere *precipitation* — that single
number separates a fundable company from a press release.
"""

CACHED_DRAFTS = [DRAFT_V1, DRAFT_V2]


# --- Two cached Editor evaluations (reject, then accept) -------------------

CACHED_EVALS = [
    {
        "score": 5,
        "feedback": "Too generic to ship. The investable angle is 'rare earths matter,' "
                    "which is not a thesis — name the specific signal an investor should "
                    "track. The pricing lens restates the technical point instead of "
                    "addressing price warfare. The diligence flag ('confirm it works') is "
                    "useless; demand a concrete, measurable technical milestone. Sharpen the "
                    "skepticism: the bench-scale caveat should drive the whole framing.",
    },
    {
        "score": 9,
        "feedback": "Ships. The angle is now specific and actionable (track DOE Title XVII "
                    "filing / offtake as the validation signal). The diligence flag demands "
                    "a real number (kg/hr) and the separation-vs-precipitation distinction — "
                    "mechanism-level skepticism. The pricing lens does real work on margin "
                    "compression. Holds the tension without collapsing into a flat bull/bear call.",
    },
]


# --- Stand-in agents that read the cache instead of calling the model ------

def demo_analyze(brief: Brief) -> Brief:
    time.sleep(STEP_PAUSE)
    brief.findings = [Finding(**f) for f in CACHED_FINDINGS]
    return brief


def demo_write(brief: Brief) -> Brief:
    time.sleep(STEP_PAUSE)
    # revision_count is 0 for the first draft, 1 for the revision, etc.
    index = min(brief.revision_count, len(CACHED_DRAFTS) - 1)
    brief.draft = CACHED_DRAFTS[index]
    return brief


def demo_edit(brief: Brief) -> Brief:
    time.sleep(STEP_PAUSE)
    # The editor runs once per draft; pick the matching cached evaluation.
    index = min(brief.revision_count - 1, len(CACHED_EVALS) - 1)
    index = max(index, 0)
    brief.editor_score = CACHED_EVALS[index]["score"]
    brief.editor_feedback = CACHED_EVALS[index]["feedback"]
    return brief
    