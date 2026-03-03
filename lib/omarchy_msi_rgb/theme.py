"""
Omarchy theme color reader.

Reads the current theme's colors.toml and provides color values
as (R, G, B) tuples for use by the pattern engine.
"""

import os
from pathlib import Path

# Default paths
THEME_COLORS_PATH = Path.home() / ".config" / "omarchy" / "current" / "theme" / "colors.toml"
THEME_NAME_PATH = Path.home() / ".config" / "omarchy" / "current" / "theme.name"

# The 20 standard color variables in an omarchy theme
COLOR_VARIABLES = [
    "accent",
    "cursor",
    "foreground",
    "background",
    "selection_foreground",
    "selection_background",
    "color0", "color1", "color2", "color3",
    "color4", "color5", "color6", "color7",
    "color8", "color9", "color10", "color11",
    "color12", "color13", "color14", "color15",
]

# Semantic groupings for the TUI
COLOR_GROUPS = {
    "Theme": ["accent", "cursor", "foreground", "background",
              "selection_foreground", "selection_background"],
    "Normal": ["color0", "color1", "color2", "color3",
               "color4", "color5", "color6", "color7"],
    "Bright": ["color8", "color9", "color10", "color11",
               "color12", "color13", "color14", "color15"],
}


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert '#RRGGBB' or 'RRGGBB' hex string to (R, G, B) tuple."""
    h = hex_color.strip().lstrip("#")
    if len(h) != 6:
        return (0, 0, 0)
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except ValueError:
        return (0, 0, 0)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert (R, G, B) to '#RRGGBB' hex string."""
    return f"#{r:02x}{g:02x}{b:02x}"


def load_theme_colors(path: Path | str | None = None) -> dict[str, tuple[int, int, int]]:
    """
    Load the current omarchy theme colors.

    Returns a dict mapping color variable names to (R, G, B) tuples.
    Falls back to sensible defaults if the theme file can't be read.
    """
    if path is None:
        path = THEME_COLORS_PATH
        if not path.exists():
            theme_name = get_current_theme_name()
            path = Path.home() / ".local" / "share" / "omarchy" / "themes" / theme_name / "colors.toml"
    else:
        path = Path(path)

    colors: dict[str, tuple[int, int, int]] = {}

    if not path.exists():
        # Return minimal defaults
        return _default_colors()

    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue

                key, _, value = line.partition("=")
                key = key.strip().strip("\"'")
                value = value.strip()

                # Extract value between quotes
                if '"' in value:
                    value = value.split('"')[1]
                elif "'" in value:
                    value = value.split("'")[1]

                if key and value:
                    colors[key] = hex_to_rgb(value)
    except (IOError, OSError):
        return _default_colors()

    # Fill in any missing standard variables with defaults
    defaults = _default_colors()
    for var in COLOR_VARIABLES:
        if var not in colors:
            colors[var] = defaults.get(var, (128, 128, 128))

    return colors


def get_current_theme_name() -> str:
    """Get the name of the currently active omarchy theme."""
    try:
        return THEME_NAME_PATH.read_text().strip()
    except (IOError, OSError):
        return "unknown"


def _default_colors() -> dict[str, tuple[int, int, int]]:
    """Fallback colors if no theme is loaded."""
    return {
        "accent": (137, 180, 250),
        "cursor": (245, 224, 220),
        "foreground": (205, 214, 244),
        "background": (30, 30, 46),
        "selection_foreground": (30, 30, 46),
        "selection_background": (245, 224, 220),
        "color0": (69, 71, 90),
        "color1": (243, 139, 168),
        "color2": (166, 227, 161),
        "color3": (249, 226, 175),
        "color4": (137, 180, 250),
        "color5": (245, 194, 231),
        "color6": (148, 226, 213),
        "color7": (186, 194, 222),
        "color8": (88, 91, 112),
        "color9": (243, 139, 168),
        "color10": (166, 227, 161),
        "color11": (249, 226, 175),
        "color12": (137, 180, 250),
        "color13": (245, 194, 231),
        "color14": (148, 226, 213),
        "color15": (166, 173, 200),
    }
