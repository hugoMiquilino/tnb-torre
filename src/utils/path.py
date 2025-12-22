import sys
from pathlib import Path

def resource_path(relative_path: str) -> Path:
    # .exe
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    # .py 
    return Path(relative_path)
