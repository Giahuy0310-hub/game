import time

_state = {
    "target_text": "",
    "typed_text": "",
    "start_time": None,
    "end_time": None,
    "is_running": False,
    "time_limit": None,
}

def is_completed():
    return _state["typed_text"] == _state["target_text"]

def get_target_text():
    return _state["target_text"]

def get_typed_text():
    return _state["typed_text"]

def update_typed(typed_text):

    if not _state["is_running"]:
        return

    if is_time_up():
        return

    if _state["start_time"] is None and typed_text:
        _state["start_time"] = time.time()

    _state["typed_text"] = typed_text

    if typed_text.strip() == _state["target_text"].strip():
        end_session()
        return

def start_session(target_text, time_limit=None):
    _state["target_text"] = target_text
    _state["typed_text"] = ""
    _state["start_time"] = None
    _state["end_time"] = None
    _state["is_running"] = True
    _state["time_limit"] = time_limit


def end_session():
    if _state["is_running"]:
        _state["end_time"] = time.time()
        _state["is_running"] = False


def reset():
    _state["target_text"] = ""
    _state["typed_text"] = ""
    _state["start_time"] = None
    _state["end_time"] = None
    _state["is_running"] = False
    _state["time_limit"] = None

def get_elapsed_time():
    if _state["start_time"] is None:
        return 0.0
    end = _state["end_time"] if _state["end_time"] else time.time()
    return round(end - _state["start_time"], 2)
    if elapsed < 1:
        return 0.0


def get_remaining_time():
    if _state["time_limit"] is None:
        return None
    return max(0.0, round(_state["time_limit"] - get_elapsed_time(), 2))


def is_time_up():
    remaining = get_remaining_time()
    return False if remaining is None else remaining <= 0


def get_char_status():
    result = []
    target = _state["target_text"]
    typed = _state["typed_text"]
    for i, ch in enumerate(target):
        if i < len(typed):
            status = "correct" if typed[i] == ch else "wrong"
        else:
            status = "pending"
        result.append({"char": ch, "status": status})
    return result


def count_errors():
    target = _state["target_text"]
    typed = _state["typed_text"]
    errors = 0
    for i, ch in enumerate(typed):
        if i < len(target):
            if ch != target[i]:
                errors += 1
        else:
            errors += 1
    return errors


def count_correct_chars():
    target = _state["target_text"]
    typed = _state["typed_text"]
    return sum(1 for i, ch in enumerate(typed) if i < len(target) and ch == target[i])


def get_wpm():
    elapsed = get_elapsed_time()
    if elapsed == 0:
        return 0.0
    return round((count_correct_chars() / 5) / (elapsed / 60), 1)


def get_cpm():
    elapsed = get_elapsed_time()
    if elapsed == 0:
        return 0.0
    return round(count_correct_chars() / (elapsed / 60), 1)


def get_accuracy():
    total = len(_state["typed_text"])
    if total == 0:
        return 100.0
    return round((count_correct_chars() / total) * 100, 1)


def get_result():
    return {
        "wpm": get_wpm(),
        "cpm": get_cpm(),
        "accuracy": get_accuracy(),
        "errors": count_errors(),
        "correct_chars": count_correct_chars(),
        "elapsed_time": get_elapsed_time(),
        "target_length": len(_state["target_text"]),
        "typed_length": len(_state["typed_text"]),
        "completed": _state["typed_text"] == _state["target_text"],
    }


def get_realtime_stats():
    return {
        "wpm": get_wpm(),
        "cpm": get_cpm(),
        "accuracy": get_accuracy(),
        "errors": count_errors(),
        "elapsed": get_elapsed_time(),
        "remaining": get_remaining_time(),
        "time_up": is_time_up(),
        "char_status": get_char_status(),
        "is_running": _state["is_running"],
    }
