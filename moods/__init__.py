"""Deterministic player-mood labels from game telemetry, with strictly grounded narration."""
from .classify import Config, LevelSummary, summarise_levels, classify_level, player_profile
from .narrate import facts_for, template_narration, ungrounded_numbers, narrate

__all__ = [
    "Config", "LevelSummary", "summarise_levels", "classify_level", "player_profile",
    "facts_for", "template_narration", "ungrounded_numbers", "narrate",
]
