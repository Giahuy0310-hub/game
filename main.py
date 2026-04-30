import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import show_menu, root

if __name__ == "__main__":
    show_menu()
    root.mainloop()