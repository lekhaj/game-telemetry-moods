from __future__ import annotations

import json
import re
from typing import Callable, Optional


def facts_for(player: str, profile: dict) -> dict:
    """The ONLY data a narrator may use. Flat, small, and checkable."""
    return {
        "player": player,
        "levels_played": profile["levels_played"],
        "frustrated_levels": profile["moods"].get("frustrated", 0),
        "flow_levels": profile["moods"].get("flow", 0),
        "mastery_levels": profile["moods"].get("mastery", 0),
        "hardest_level": profile["hardest_level"],
        "hardest_level_fails": profile["hardest_level_fails"],
        "at_risk": profile["at_risk"],
    }


def template_narration(f: dict) -> str:
    """Deterministic fallback: always grounded, no model needed."""
    parts = [f"{f['player']} played {f['levels_played']} level(s)."]
    if f["frustrated_levels"]:
        parts.append(
            f"They struggled on {f['frustrated_levels']} level(s); the hardest was level "
            f"{f['hardest_level']} with {f['hardest_level_fails']} fails."
        )
    if f["mastery_levels"]:
        parts.append(f"They overcame {f['mastery_levels']} level(s) after failing first.")
    if f["flow_levels"]:
        parts.append(f"{f['flow_levels']} level(s) went smoothly.")
    if f["at_risk"]:
        parts.append("Worth a nudge: they may churn.")
    return " ".join(parts)


_NUM = re.compile(r"\d+(?:\.\d+)?")


def ungrounded_numbers(text: str, facts: dict) -> list:
    """Numbers in the text that do not appear in the facts. Empty list == grounded."""
    allowed = {str(v) for v in facts.values() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    return [n for n in _NUM.findall(text) if n not in allowed]


def narrate(facts: dict, llm: Optional[Callable[[str], str]] = None) -> tuple:
    """Use the LLM for fluent prose, but only keep it if every number is grounded in the facts.

    Returns (text, source) where source is 'llm' or 'template'.
    """
    if llm is not None:
        prompt = (
            "Write 2 sentences about this player using ONLY these facts. "
            "Do not add any number that is not in the facts.\n" + json.dumps(facts)
        )
        text = llm(prompt)
        if not ungrounded_numbers(text, facts):
            return text, "llm"
    return template_narration(facts), "template"
