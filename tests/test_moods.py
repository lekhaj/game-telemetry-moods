import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from moods import summarise_levels, classify_level, player_profile, facts_for, ungrounded_numbers, narrate  # noqa: E402


def ev(name, t, level=1, player="p"):
    return dict(player=player, level=level, name=name, t=t)


def level(events):
    return classify_level(summarise_levels(events)[0])


def test_frustrated_after_fail_streak():
    s = level([ev("level_start", 0), ev("level_fail", 5), ev("level_start", 6), ev("level_fail", 9),
               ev("level_start", 10), ev("level_fail", 14)])
    assert s.mood == "frustrated"


def test_mastery_after_failures_then_win():
    s = level([ev("level_start", 0), ev("level_fail", 5), ev("level_start", 6), ev("level_fail", 9),
               ev("level_start", 10), ev("level_win", 30)])
    assert s.mood == "mastery"


def test_bored_on_instant_first_try_win():
    assert level([ev("level_start", 0), ev("level_win", 8)]).mood == "bored"


def test_flow_on_normal_win():
    assert level([ev("level_start", 0), ev("level_win", 60)]).mood == "flow"


def test_quit_after_single_fail_is_frustrated():
    assert level([ev("level_start", 0), ev("level_fail", 5), ev("quit", 6)]).mood == "frustrated"


def test_grounding_check_rejects_invented_numbers():
    f = {"levels_played": 4, "hardest_level": 2}
    assert ungrounded_numbers("played 4 levels", f) == []
    assert ungrounded_numbers("played 40 levels", f) == ["40"]


def test_narrate_falls_back_when_llm_hallucinates():
    prof = player_profile(summarise_levels([ev("level_start", 0), ev("level_win", 60)]))["p"]
    f = facts_for("p", prof)
    assert narrate(f, llm=lambda p: "p played 77 levels")[1] == "template"
    assert narrate(f, llm=lambda p: "p played 1 level smoothly")[1] == "llm"
