"""
Configuration persistence for omarchy-msi-rgb.

Reads the user's pattern/brightness preferences from
~/.config/omarchy/msi-rgb.toml

Colors are always derived from the active omarchy theme:
  keyboard primary = accent, secondary = color1
  lightbar = accent
"""

from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "omarchy" / "msi-rgb.toml"

DEFAULT_CONFIG = {
    "keyboard": {
        "pattern": "gradient-h",
        "brightness": 100,
    },
    "lightbar": {
        "brightness": 100,
    },
}


def load_config(path: Path | str | None = None) -> dict:
    """
    Load the MSI RGB configuration.

    Returns a dict with 'keyboard' and 'lightbar' sections.
    Falls back to defaults if the config file doesn't exist.
    """
    if path is None:
        path = CONFIG_PATH
    else:
        path = Path(path)

    config = _deep_copy(DEFAULT_CONFIG)

    if not path.exists():
        return config

    try:
        parsed = _simple_toml_parse(path.read_text())
        for section in ("keyboard", "lightbar"):
            if section in parsed:
                for key, value in parsed[section].items():
                    if key in config.get(section, {}):
                        config[section][key] = value
    except (IOError, OSError, ValueError):
        pass

    return config


def _deep_copy(d: dict) -> dict:
    """Simple deep copy for nested dicts with primitive values."""
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = _deep_copy(v)
        else:
            result[k] = v
    return result


def _simple_toml_parse(text: str) -> dict:
    """Minimal TOML parser — no external dependencies."""
    result: dict = {}
    current_section = None

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip()
            result[current_section] = {}
            continue

        if "=" in line and current_section:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            try:
                value = int(value)
            except ValueError:
                pass

            result[current_section][key] = value

    return result
