"""Generate synthetic telemetry, label moods, and narrate. Runs offline.

    python examples/demo.py
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from moods import summarise_levels, player_profile, facts_for, narrate  # noqa: E402

random.seed(3)


def synth(player: str, skill: float, levels: int = 5):
    events, t = [], 0.0
    for lv in range(1, levels + 1):
        difficulty = 0.15 * lv
        for _ in range(8):
            events.append(dict(player=player, level=lv, name="level_start", t=t)); t += random.uniform(8, 40)
            if random.random() < max(0.05, skill - difficulty):
                events.append(dict(player=player, level=lv, name="level_win", t=t)); t += 2
                break
            events.append(dict(player=player, level=lv, name="level_fail", t=t)); t += 2
        else:
            events.append(dict(player=player, level=lv, name="quit", t=t))
            return events
    return events


events = synth("ana", 0.95) + synth("ben", 0.55) + synth("chi", 0.30)
for player, prof in player_profile(summarise_levels(events)).items():
    text, source = narrate(facts_for(player, prof))
    print(f"[{source}] {text}\n   moods={prof['moods']}")

# A hallucinating "LLM" is rejected because it invents a number:
bad_llm = lambda prompt: "ana played 99 levels and was delighted."
f = facts_for("ana", player_profile(summarise_levels(events))["ana"])
print("\nhallucinated narration ->", narrate(f, llm=bad_llm)[1])
