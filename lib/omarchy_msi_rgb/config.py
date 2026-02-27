"""
Configuration persistence for omarchy-msi-rgb.

Reads and writes the user's pattern/color preferences to
~/.config/omarchy/msi-rgb.toml
"""

import os
from pathlib import Path

try:
    import tomlkit
    HAS_TOMLKIT = True
except ImportError:
    HAS_TOMLKIT = False

CONFIG_PATH = Path.home() / ".config" / "omarchy" / "msi-rgb.toml"

DEFAULT_CONFIG = {
    "keyboard": {
        "pattern": "gradient-h",
        "primary": "accent",
        "secondary": "color1",
        "brightness": 100,
    },
    "lightbar": {
        "pattern": "solid",
        "color": "accent",
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
        text = path.read_text()
        if HAS_TOMLKIT:
            parsed = tomlkit.parse(text)
        else:
            parsed = _simple_toml_parse(text)

        # Merge parsed values over defaults
        for section in ("keyboard", "lightbar"):
            if section in parsed:
                for key, value in parsed[section].items():
                    if key in config.get(section, {}):
                        config[section][key] = value

    except (IOError, OSError, ValueError):
        pass

    return config


def save_config(config: dict, path: Path | str | None = None):
    """Save the MSI RGB configuration."""
    if path is None:
        path = CONFIG_PATH
    else:
        path = Path(path)

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    if HAS_TOMLKIT:
        doc = tomlkit.document()
        doc.add(tomlkit.comment("omarchy-msi-rgb configuration"))
        doc.add(tomlkit.comment("Pattern and color settings for MSI SteelSeries RGB"))
        doc.add(tomlkit.nl())

        for section_name in ("keyboard", "lightbar"):
            section = config.get(section_name, {})
            table = tomlkit.table()
            for key, value in section.items():
                table.add(key, value)
            doc.add(section_name, table)
            doc.add(tomlkit.nl())

        path.write_text(tomlkit.dumps(doc))
    else:
        _simple_toml_write(config, path)


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
    """Minimal TOML parser for when tomlkit isn't available."""
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

            # Try to parse as int
            try:
                value = int(value)
            except ValueError:
                pass

            result[current_section][key] = value

    return result


def _simple_toml_write(config: dict, path: Path):
    """Minimal TOML writer for when tomlkit isn't available."""
    lines = [
        "# omarchy-msi-rgb configuration",
        "# Pattern and color settings for MSI SteelSeries RGB",
        "",
    ]
    for section_name, section in config.items():
        if isinstance(section, dict):
            lines.append(f"[{section_name}]")
            for key, value in section.items():
                if isinstance(value, str):
                    lines.append(f'{key} = "{value}"')
                else:
                    lines.append(f"{key} = {value}")
            lines.append("")

    path.write_text("\n".join(lines) + "\n")
