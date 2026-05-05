import tkinter as tk
from tkinter import ttk
import sys
import os

try:
    import winsound
    def play_sound(is_correct):
        if is_correct:
            winsound.Beep(800, 50)
        else:
            winsound.Beep(400, 150)
except ImportError:
    def play_sound(is_correct):
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.text_engine import load_data, get_challenge
import modules.typing_engine as engine
from modules.stats_system import save_result, get_leaderboard, get_player_history, get_player_stats

TICK_MS = 100

BG      = "#1e1e2e"
SURFACE = "#313244"
PRIMARY = "#cba6f7"
GREEN   = "#a6e3a1"
RED     = "#f38ba8"
YELLOW  = "#f9e2af"
TEXT    = "#cdd6f4"
SUBTEXT = "#a6adc8"
PENDING = "#585b70"

MONO  = ("Consolas", 14)
UI    = ("Segoe UI", 11)
BOLD  = ("Segoe UI", 13, "bold")
TITLE = ("Segoe UI", 20, "bold")

root = tk.Tk()
root.configure(bg=BG)
root.resizable(True, True)
root.geometry("650x650")
root.state('zoomed')

data_dict      = load_data()
player_name    = tk.StringVar(value="Player")
level_var      = tk.StringVar(value="easy")
mode_var       = tk.StringVar(value="sentence")
timed_var      = tk.BooleanVar(value=False)
time_limit     = tk.IntVar(value=60)
input_var      = tk.StringVar()
char_labels    = []
tick_job       = [None]
input_trace_id = [None]

wpm_lbl = acc_lbl = err_lbl = timer_lbl = progress = input_box = None


def clear_screen():
    try:
        for w in root.winfo_children():
            w.destroy()
    except tk.TclError:
        pass


def lbl(parent, text, font=None, color=None, **kw):
    return tk.Label(parent, text=text, font=font or UI,
                    fg=color or TEXT, bg=parent.cget("bg"), **kw)


def btn(parent, text, cmd, color=None):
    return tk.Button(parent, text=text, command=cmd, font=UI,
                     fg=BG, bg=color or PRIMARY,
                     activebackground=SUBTEXT,
                     relief="flat", cursor="hand2", padx=16, pady=6)


def surface(parent, **kw):
    return tk.Frame(parent, bg=SURFACE, **kw)


def show_menu():
    if tick_job[0]:
        root.after_cancel(tick_job[0])
        tick_job[0] = None
    if input_trace_id[0]:
        input_var.trace_remove("write", input_trace_id[0])
        input_trace_id[0] = None
    engine.reset()
    clear_screen()
    root.title("Typing Speed Game")

    outer = tk.Frame(root, bg=BG)
    outer.place(relx=0.5, rely=0.5, anchor="center")

    lbl(outer, "⌨  Typing Speed Game", font=TITLE, color=PRIMARY).pack(pady=(0, 4))
    lbl(outer, "Luyện tốc độ gõ phím", color=SUBTEXT).pack()

    card = surface(outer, padx=30, pady=18)
    card.pack(pady=18, padx=40, fill="x")

    r1 = tk.Frame(card, bg=SURFACE)
    r1.pack(fill="x", pady=6)
    lbl(r1, "Tên người chơi:", color=SUBTEXT).pack(side="left")
    tk.Entry(r1, textvariable=player_name, font=UI,
             bg=BG, fg=TEXT, insertbackground=TEXT, relief="flat", width=20).pack(side="right")

    r2 = tk.Frame(card, bg=SURFACE)
    r2.pack(fill="x", pady=6)
    lbl(r2, "Cấp độ:", color=SUBTEXT).pack(side="left")
    for val, txt in [("easy", "Dễ"), ("medium", "Trung bình"), ("hard", "Khó")]:
        tk.Radiobutton(r2, text=txt, variable=level_var, value=val,
                       bg=SURFACE, fg=TEXT, selectcolor=BG,
                       activebackground=SURFACE, font=UI).pack(side="right", padx=6)

    r3 = tk.Frame(card, bg=SURFACE)
    r3.pack(fill="x", pady=6)
    lbl(r3, "Chế độ:", color=SUBTEXT).pack(side="left")
    for val, txt in [("sentence", "Câu đơn"), ("paragraph", "Đoạn văn")]:
        tk.Radiobutton(r3, text=txt, variable=mode_var, value=val,
                       bg=SURFACE, fg=TEXT, selectcolor=BG,
                       activebackground=SURFACE, font=UI).pack(side="right", padx=6)

    r4 = tk.Frame(card, bg=SURFACE)
    r4.pack(fill="x", pady=6)
    tk.Checkbutton(r4, text="Timed Challenge", variable=timed_var,
                   bg=SURFACE, fg=YELLOW, selectcolor=BG,
                   activebackground=SURFACE, font=UI).pack(side="left")
    tk.Spinbox(r4, from_=15, to=300, increment=15, textvariable=time_limit,
               width=5, font=UI, bg=BG, fg=TEXT,
               buttonbackground=SURFACE).pack(side="right")
    lbl(r4, "giây", color=SUBTEXT).pack(side="right", padx=4)

    br = tk.Frame(outer, bg=BG)
    br.pack(pady=10)
    btn(br, "▶  Bắt đầu", start_game).pack(side="left", padx=8)
    btn(br, "🏆  Bảng xếp hạng", show_leaderboard, color=YELLOW).pack(side="left", padx=8)
    btn(br, "📊  Lịch sử của tôi", show_history, color=GREEN).pack(side="left", padx=8)


def start_game():
    sentence = get_challenge(data_dict, level_var.get(), mode_var.get())
    limit = time_limit.get() if timed_var.get() else None
    engine.start_session(sentence, time_limit=limit)
    show_game_screen(sentence)


def show_game_screen(sentence):
    global wpm_lbl, acc_lbl, err_lbl, timer_lbl, progress, input_box, char_labels
    clear_screen()
    root.title("Đang chơi...")

    top = tk.Frame(root, bg=BG)
    top.pack(fill="x", padx=20, pady=(14, 0))
    lbl(top, f"Level: {level_var.get().upper()}  |  Mode: {mode_var.get()}", color=SUBTEXT).pack(side="left")
    btn(top, "✕ Thoát", show_menu, color=RED).pack(side="right")

    timer_lbl = lbl(root, "⏱  0.0s", font=BOLD, color=YELLOW)
    timer_lbl.pack(pady=(10, 0))

    sr = tk.Frame(root, bg=BG)
    sr.pack(pady=4)
    wpm_lbl = lbl(sr, "WPM: 0", font=BOLD, color=PRIMARY)
    wpm_lbl.pack(side="left", padx=20)
    acc_lbl = lbl(sr, "ACC: 100%", font=BOLD, color=GREEN)
    acc_lbl.pack(side="left", padx=20)
    err_lbl = lbl(sr, "Lỗi: 0", font=BOLD, color=RED)
    err_lbl.pack(side="left", padx=20)

    pb_frame = tk.Frame(root, bg=BG)
    pb_frame.pack(fill="x", padx=20, pady=6)
    progress = ttk.Progressbar(pb_frame, mode="determinate")
    progress.pack(fill="x")

    tf = surface(root, padx=16, pady=14)
    tf.pack(padx=20, fill="x")

    root.update_idletasks()
    _tmp = tk.Label(tf, text="A", font=MONO, bg=SURFACE)
    _tmp.pack()
    root.update_idletasks()
    FONT_W = _tmp.winfo_reqwidth()
    AREA_W = tf.winfo_width() - 32
    if AREA_W < 200:
        AREA_W = root.winfo_width() - 80
    MAX_COL = max(20, AREA_W // FONT_W)
    _tmp.destroy()

    wrap = tk.Frame(tf, bg=SURFACE)
    wrap.pack(anchor="w")

    char_labels = []
    current_len = 0
    words       = sentence.split(" ")

    row_frame = tk.Frame(wrap, bg=SURFACE)
    row_frame.pack(anchor="w")

    for word_index, word in enumerate(words):
        if current_len > 0 and current_len + len(word) > MAX_COL:
            row_frame = tk.Frame(wrap, bg=SURFACE)
            row_frame.pack(anchor="w")
            current_len = 0

        for ch in word:
            c = tk.Label(row_frame, text=ch, font=MONO, fg=PENDING, bg=SURFACE)
            c.pack(side="left")
            char_labels.append(c)
            current_len += 1

        if word_index < len(words) - 1:
            c = tk.Label(row_frame, text=" ", font=MONO, fg=PENDING, bg=SURFACE)
            c.pack(side="left")
            char_labels.append(c)
            current_len += 1

    input_var.set("")
    input_trace_id[0] = input_var.trace_add("write", on_type)
    input_box = tk.Entry(root, textvariable=input_var, font=MONO,
                         bg=SURFACE, fg=TEXT, insertbackground=PRIMARY,
                         relief="flat")
    input_box.pack(fill="x", padx=20, pady=14, ipady=8)
    input_box.focus()
    input_box.bind("<Control-v>", lambda e: "break")
    input_box.bind("<Control-V>", lambda e: "break")
    root.bind("<Escape>", lambda e: show_menu()) 
    root.bind("<F5>", lambda e: start_game())     
    # -----------------------
    tick()

def on_type(*_):
    typed = input_var.get()
    engine.update_typed(typed)
    stats = engine.get_realtime_stats()

    char_status = stats["char_status"]
    if typed and len(char_status) >= len(typed):
        play_sound(char_status[len(typed)-1]["status"] == "correct")

    for i, c in enumerate(char_labels):
        if i < len(stats["char_status"]):
            st = stats["char_status"][i]["status"]
            color = GREEN if st == "correct" else (RED if st == "wrong" else PENDING)
            try:
                c.config(fg=color)
            except tk.TclError:
                return

    try:
        pct = (len(typed) / max(1, len(engine._state["target_text"]))) * 100
        progress["value"] = min(pct, 100)
    except tk.TclError:
        return

    if not stats["is_running"]:
        finish_game()

def tick():
    stats = engine.get_realtime_stats()
    if not stats["is_running"] and engine._state["start_time"] is None:
        tick_job[0] = root.after(TICK_MS, tick)
        return
    if not stats["is_running"]:
        return

    remaining = stats["remaining"]
    if remaining is not None:
        timer_lbl.config(text=f"⏱  {remaining:.1f}s còn lại",
                         fg=RED if remaining < 10 else YELLOW)
        if stats["time_up"]:
            engine.end_session()
            finish_game()
            return
    else:
        timer_lbl.config(text=f"⏱  {stats['elapsed']:.1f}s")

    wpm_lbl.config(text=f"WPM: {stats['wpm']}")
    acc_lbl.config(text=f"ACC: {stats['accuracy']}%")
    err_lbl.config(text=f"Lỗi: {stats['errors']}")
    tick_job[0] = root.after(TICK_MS, tick)


def finish_game():
    if tick_job[0]:
        root.after_cancel(tick_job[0])
        tick_job[0] = None
    if input_trace_id[0]:
        input_var.trace_remove("write", input_trace_id[0])
        input_trace_id[0] = None
    if input_box:
        try:
            input_box.config(state="disabled")
        except tk.TclError:
            pass

    result = engine.get_result()
    save_result(result, player_name.get(), level_var.get(), mode_var.get())
    show_result_screen(result)


def show_result_screen(result):
    clear_screen()
    root.title("Kết quả")

    outer = tk.Frame(root, bg=BG)
    outer.place(relx=0.5, rely=0.5, anchor="center")

    completed = result.get("completed", False)
    title_txt = "✅  Hoàn thành!" if completed else "⏰  Hết giờ!"
    color = GREEN if completed else YELLOW
    lbl(outer, title_txt, font=TITLE, color=color).pack(pady=(0, 6))

    card = surface(outer, padx=40, pady=20)
    card.pack(pady=10, fill="x")

    rows = [
        ("WPM",       str(result["wpm"]),           PRIMARY),
        ("CPM",       str(result["cpm"]),            PRIMARY),
        ("Accuracy",  f"{result['accuracy']}%",      GREEN),
        ("Lỗi",       str(result["errors"]),         RED),
        ("Thời gian", f"{result['elapsed_time']}s", YELLOW),
    ]
    for label, val, col in rows:
        r = tk.Frame(card, bg=SURFACE)
        r.pack(fill="x", pady=4)
        lbl(r, label, color=SUBTEXT).pack(side="left")
        tk.Label(r, text=val, font=BOLD, fg=col, bg=SURFACE).pack(side="right")

    br = tk.Frame(outer, bg=BG)
    br.pack(pady=16)
    btn(br, "🔁  Chơi lại", start_game).pack(side="left", padx=8)
    btn(br, "🏠  Menu", show_menu, color=SUBTEXT).pack(side="left", padx=8)
    btn(br, "🏆  Xếp hạng", show_leaderboard, color=YELLOW).pack(side="left", padx=8)


def show_leaderboard():
    clear_screen()
    root.title("Bảng xếp hạng")

    lbl(root, "🏆  Bảng Xếp Hạng", font=TITLE, color=YELLOW).pack(pady=(22, 4))

    filter_level = tk.StringVar(value="all")

    fr = tk.Frame(root, bg=BG)
    fr.pack()

    def refresh():
        lv = None if filter_level.get() == "all" else filter_level.get()
        board = get_leaderboard(top_n=15, level=lv)
        for row in tree.get_children():
            tree.delete(row)
        for i, e in enumerate(board, 1):
            tree.insert("", "end", values=(
                i, e["player"], e["level"].upper(),
                e["wpm"], f"{e['accuracy']}%", e["date"][:10]
            ))

    for val, txt in [("all", "Tất cả"), ("easy", "Dễ"), ("medium", "TB"), ("hard", "Khó")]:
        tk.Radiobutton(fr, text=txt, variable=filter_level, value=val, command=refresh,
                       bg=BG, fg=TEXT, selectcolor=BG, font=UI).pack(side="left", padx=8)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background=SURFACE, foreground=TEXT,
                    fieldbackground=SURFACE, rowheight=26, font=UI)
    style.configure("Treeview.Heading", background=BG, foreground=PRIMARY, font=BOLD)

    cols = ("#", "Người chơi", "Level", "WPM", "Accuracy", "Ngày")
    tree = ttk.Treeview(root, columns=cols, show="headings", height=15)
    for col, w in zip(cols, [40, 200, 100, 100, 110, 140]):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center")
    tree.pack(padx=40, pady=10, fill="x")
    refresh()

    btn(root, "← Quay lại", show_menu, color=SUBTEXT).pack(pady=6)


def show_history():
    clear_screen()
    root.title("Lịch sử")

    name = player_name.get()
    lbl(root, f"📊  Lịch sử — {name}", font=TITLE, color=GREEN).pack(pady=(22, 4))

    stats = get_player_stats(name)
    if stats:
        sf = surface(root, padx=20, pady=10)
        sf.pack(padx=40, fill="x")
        info_rows = [
            ("Tổng phiên",     stats["total_sessions"]),
            ("Hoàn thành",     stats["completed_sessions"]),
            ("WPM tốt nhất",   stats["best_wpm"]),
            ("WPM trung bình", stats["avg_wpm"]),
            ("Accuracy TB",    f"{stats['avg_accuracy']}%"),
        ]
        row_frame = tk.Frame(sf, bg=SURFACE)
        row_frame.pack()
        for k, v in info_rows:
            tk.Label(row_frame, text=f"{k}: {v}", font=UI,
                     fg=PRIMARY, bg=SURFACE, padx=14).pack(side="left")

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background=SURFACE, foreground=TEXT,
                    fieldbackground=SURFACE, rowheight=26, font=UI)
    style.configure("Treeview.Heading", background=BG, foreground=PRIMARY, font=BOLD)

    cols = ("#", "Level", "WPM", "CPM", "Accuracy", "Lỗi", "TG(s)", "Ngày")
    tree = ttk.Treeview(root, columns=cols, show="headings", height=15)
    for col, w in zip(cols, [40, 90, 90, 90, 100, 70, 80, 150]):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center")
    tree.pack(padx=40, pady=8, fill="x")

    history = get_player_history(name)
    for i, e in enumerate(history, 1):
        tree.insert("", "end", values=(
            i, e["level"].upper(), e["wpm"], e["cpm"],
            f"{e['accuracy']}%", e["errors"], e["elapsed_time"], e["date"][:10]
        ))

    btn(root, "← Quay lại", show_menu, color=SUBTEXT).pack(pady=6)


show_menu()
root.mainloop()
