from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Config:
    """Every threshold lives here, so labels are explainable and tunable per game."""

    frustration_fail_streak: int = 3   # consecutive fails with no win
    flow_max_attempts: int = 3         # won within this many tries
    bored_win_seconds: float = 20.0    # first-try win faster than this
    mastery_min_fails: int = 2         # recovered after at least this many fails


@dataclass
class LevelSummary:
    player: str
    level: int
    attempts: int = 0
    fails: int = 0
    wins: int = 0
    max_fail_streak: int = 0
    quit_after_fail: bool = False
    first_win_seconds: float | None = None
    mood: str = ""
    reason: str = ""


def summarise_levels(events: list) -> list:
    """events: dicts with player, level, name (level_start|level_win|level_fail|quit), t (seconds)."""
    by_key = defaultdict(list)
    for e in sorted(events, key=lambda e: e["t"]):
        by_key[(e["player"], e["level"])].append(e)

    out = []
    for (player, level), evs in by_key.items():
        s = LevelSummary(player, level)
        streak, started_at, last = 0, None, None
        for e in evs:
            n = e["name"]
            if n == "level_start":
                s.attempts += 1
                started_at = e["t"]
            elif n == "level_fail":
                s.fails += 1
                streak += 1
                s.max_fail_streak = max(s.max_fail_streak, streak)
            elif n == "level_win":
                s.wins += 1
                streak = 0
                if s.first_win_seconds is None and started_at is not None:
                    s.first_win_seconds = e["t"] - started_at
            last = n
        s.quit_after_fail = last in ("level_fail", "quit") and s.wins == 0 and s.fails > 0
        out.append(s)
    return out


def classify_level(s: LevelSummary, cfg: Config = Config()) -> LevelSummary:
    """Rules are checked in priority order; the first match wins and records why."""
    if s.wins == 0 and (s.max_fail_streak >= cfg.frustration_fail_streak or s.quit_after_fail):
        s.mood, s.reason = "frustrated", f"{s.fails} fails, no win" + (", then left" if s.quit_after_fail else "")
    elif s.wins and s.fails >= cfg.mastery_min_fails:
        s.mood, s.reason = "mastery", f"won after {s.fails} fails"
    elif s.wins and s.attempts == 1 and (s.first_win_seconds or 1e9) < cfg.bored_win_seconds:
        s.mood, s.reason = "bored", f"first-try win in {s.first_win_seconds:.0f}s"
    elif s.wins and s.attempts <= cfg.flow_max_attempts:
        s.mood, s.reason = "flow", f"won in {s.attempts} attempt(s)"
    else:
        s.mood, s.reason = "neutral", "no strong signal"
    return s


def player_profile(summaries: list, cfg: Config = Config()) -> dict:
    """Roll level moods up to one player: counts per mood, plus the single hardest level."""
    per_player = defaultdict(list)
    for s in summaries:
        per_player[s.player].append(classify_level(s, cfg))
    profiles = {}
    for player, levels in per_player.items():
        counts = defaultdict(int)
        for lv in levels:
            counts[lv.mood] += 1
        hardest = max(levels, key=lambda lv: (lv.fails, lv.level))
        profiles[player] = {
            "levels_played": len(levels),
            "moods": dict(counts),
            "hardest_level": hardest.level,
            "hardest_level_fails": hardest.fails,
            "at_risk": counts["frustrated"] >= 1,
        }
    return profiles
