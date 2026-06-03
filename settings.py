import json
import os
from pathlib import Path

_DEFAULTS = {
    "last_source_dir": "",
    "last_output_dir": "",
    "print_after_merge": False,
}

def _settings_path() -> Path:
    return Path(os.environ.get("APPDATA", Path.home())) / "Samenvoeger" / "settings.json"

def load_settings() -> dict:
    try:
        path = _settings_path()
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return {**_DEFAULTS, **json.load(f)}
    except Exception:
        pass
    return dict(_DEFAULTS)

def save_settings(data: dict) -> None:
    try:
        path = _settings_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass
