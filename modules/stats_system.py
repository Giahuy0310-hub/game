import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCORES_FILE = os.path.join(BASE_DIR, "data", "scores.json")


def _load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_scores(scores):
    os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


def save_result(result, player_name="Player", level="easy", mode="sentence"):
    scores = _load_scores()
    entry = {
        "player": player_name,
        "level": level,
        "mode": mode,
        "wpm": result.get("wpm", 0),
        "cpm": result.get("cpm", 0),
        "accuracy": result.get("accuracy", 0),
        "errors": result.get("errors", 0),
        "elapsed_time": result.get("elapsed_time", 0),
        "completed": result.get("completed", False),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    scores.append(entry)
    _save_scores(scores)
    return entry


def get_all_scores_sorted():
    scores = _load_scores()
    return sorted(scores, key=lambda x: x.get("wpm", 0))


def get_leaderboard(top_n=10, level=None):
    scores = _load_scores()
    if level:
        scores = [s for s in scores if s.get("level") == level]
    completed = [s for s in scores if s.get("completed", False)]
    top = sorted(completed, key=lambda x: x.get("wpm", 0), reverse=True)[:top_n]
    return sorted(top, key=lambda x: x.get("wpm", 0))


def get_player_history(player_name):
    scores = _load_scores()
    history = [s for s in scores if s.get("player") == player_name]
    return sorted(history, key=lambda x: x.get("date", ""), reverse=True)


def get_player_stats(player_name):
    history = get_player_history(player_name)
    if not history:
        return {}
    completed = [s for s in history if s.get("completed", False)]
    all_wpm = [s["wpm"] for s in completed]
    all_acc = [s["accuracy"] for s in completed]
    return {
        "player": player_name,
        "total_sessions": len(history),
        "completed_sessions": len(completed),
        "best_wpm": max(all_wpm) if all_wpm else 0,
        "avg_wpm": round(sum(all_wpm) / len(all_wpm), 1) if all_wpm else 0,
        "avg_accuracy": round(sum(all_acc) / len(all_acc), 1) if all_acc else 0,
        "last_played": history[0].get("date", ""),
    }


def clear_all_scores():
    _save_scores([])
