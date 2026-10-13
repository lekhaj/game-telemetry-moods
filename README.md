# game-telemetry-moods

Turn raw game telemetry into **explainable player moods**, then narrate them with an LLM that is **not allowed to invent numbers**.

```
events ─▶ per-level summary ─▶ deterministic mood (rules + reason) ─▶ player profile
                                                                         │
                                       facts (flat, checkable) ◀─────────┘
                                          │
                  LLM prose ──▶ grounding check ──pass──▶ use it
                                      └────fail────▶ deterministic template
```

## The two ideas

1. **Classify deterministically, narrate with a model.** Moods (`frustrated`, `mastery`, `bored`, `flow`) come from transparent rules with every threshold in one `Config`. Each label carries a `reason` ("3 fails, no win, then left"), so designers can argue with it and tune it. No model decides who is frustrated.
2. **Grounding gate on the narrator.** The LLM only gets a small facts dict. Any number in its answer that is not in the facts is rejected and replaced by a template. Fluent prose when it is safe, plain truth when it is not.

## Run

```bash
python examples/demo.py      # synthetic telemetry, offline
python - <<'PY'              # tests, no dependencies
import sys; sys.path.insert(0, "tests")
import test_moods as t
[getattr(t, n)() for n in dir(t) if n.startswith("test_")]
print("ok")
PY
```

## Event shape
`{"player": "a", "level": 3, "name": "level_start|level_win|level_fail|quit", "t": 123.4}`. Adapt your own events to this in a few lines.

## Limits (honest)
Rules are a starting point, not a validated psychometric model. Calibrate thresholds against real sessions and player feedback before acting on the labels. The grounding check catches invented *numbers*, not every kind of wrong claim.

## License
MIT
