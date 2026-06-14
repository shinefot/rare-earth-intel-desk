from typing import Literal
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# The fixed vocabularies. Using Literal means these fields can ONLY ever hold
# one of the listed values. Anything else is rejected automatically.
# ---------------------------------------------------------------------------

ThemeType = Literal[
    "refining_chokepoint",
    "non_dilutive_funding",
    "permitting_lag",
    "predatory_pricing",
    "offtake",
    "separation_tech",
]

LensType = Literal["geopolitical", "technical", "pricing"]
ConfidenceType = Literal["low", "medium", "high"]


# ---------------------------------------------------------------------------
# A single analytical finding. The Analyst agent will produce a list of these.
# ---------------------------------------------------------------------------

class Finding(BaseModel):
    lens: LensType                      # which of the three angles this is
    claim: str                          # the actual point being made
    evidence_url: str | None = None     # optional supporting link
    confidence: ConfidenceType          # how sure the analyst is


# ---------------------------------------------------------------------------
# The Brief: our shared document. It travels through the pipeline, and each
# agent fills in its own section. Grouped below by who fills what.
# ---------------------------------------------------------------------------

class Brief(BaseModel):
    # --- filled at ingestion (the raw news item, before any agent runs) ---
    source_url: str
    raw_title: str
    raw_text: str

    # --- filled by the Triage agent ---
    is_relevant: bool | None = None
    theme: ThemeType | None = None

    # --- filled by the Analyst agent ---
    findings: list[Finding] = Field(default_factory=list)

    # --- filled by the Writer agent ---
    draft: str | None = None

    # --- filled by the Editor agent ---
    editor_score: int | None = None
    editor_feedback: str | None = None
    revision_count: int = 0


# ---------------------------------------------------------------------------
# One sample news item to use as our test input — a processing-tech
# breakthrough claim. (Hypothetical company, for testing.)
# ---------------------------------------------------------------------------

SAMPLE_NEWS = {
    "source_url": "https://example.com/helix-minerals-bioseparation",
    "raw_title": "Helix Minerals claims 99% pure dysprosium via novel bio-separation process",
    "raw_text": (
        "Texas-based startup Helix Minerals announced today that its proprietary "
        "bio-separation process has achieved 99% pure dysprosium oxide at lab scale, "
        "a result it says bypasses the traditional solvent-extraction stages that "
        "dominate rare-earth refining. The company claims its engineered microbes "
        "selectively bind heavy rare-earth elements, cutting both chemical reagent "
        "costs and acidic waste. Helix has not yet demonstrated the process beyond "
        "bench scale and has not disclosed throughput figures. The announcement "
        "follows growing U.S. policy interest in domestic heavy rare-earth capacity "
        "amid tightening Chinese export licensing."
    ),
}


# ---------------------------------------------------------------------------
# Running this file directly builds a Brief from the sample and prints it,
# so we can SEE the blueprint working.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    brief = Brief(**SAMPLE_NEWS)
    print("Brief created successfully. Here it is:\n")
    print(brief.model_dump_json(indent=2))