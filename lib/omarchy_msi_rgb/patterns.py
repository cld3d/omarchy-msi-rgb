"""
Pattern engine for generating per-key color maps from theme colors.

Each pattern function takes theme colors and configuration, then produces
a mapping of Linux keycodes to RGB color tuples. The core module then
translates these to MSI keycodes and sends them to hardware.
"""

import hashlib
import math
from typing import Callable

from .keymap import (
    LINUX_TO_MSI,
    PHYSICAL_LAYOUT,
    KEY_ALIASES,
    FN_MSI_KEYCODE,
    get_key_normalized_position,
    get_all_linux_keycodes,
)
from .theme import COLOR_VARIABLES


# --- Color math utilities ---

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b by factor t."""
    return a + (b - a) * t


def lerp_rgb(
    c1: tuple[int, int, int],
    c2: tuple[int, int, int],
    t: float,
) -> tuple[int, int, int]:
    """Linearly interpolate between two RGB colors."""
    t = max(0.0, min(1.0, t))
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )


def rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Convert RGB (0-255) to HSV (h: 0-360, s: 0-1, v: 0-1)."""
    r_, g_, b_ = r / 255.0, g / 255.0, b / 255.0
    mx = max(r_, g_, b_)
    mn = min(r_, g_, b_)
    diff = mx - mn

    if diff == 0:
        h = 0.0
    elif mx == r_:
        h = (60 * ((g_ - b_) / diff) + 360) % 360
    elif mx == g_:
        h = (60 * ((b_ - r_) / diff) + 120) % 360
    else:
        h = (60 * ((r_ - g_) / diff) + 240) % 360

    s = 0.0 if mx == 0 else diff / mx
    v = mx
    return (h, s, v)


def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    """Convert HSV (h: 0-360, s: 0-1, v: 0-1) to RGB (0-255)."""
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h < 60:
        r_, g_, b_ = c, x, 0
    elif h < 120:
        r_, g_, b_ = x, c, 0
    elif h < 180:
        r_, g_, b_ = 0, c, x
    elif h < 240:
        r_, g_, b_ = 0, x, c
    elif h < 300:
        r_, g_, b_ = x, 0, c
    else:
        r_, g_, b_ = c, 0, x

    return (
        int((r_ + m) * 255),
        int((g_ + m) * 255),
        int((b_ + m) * 255),
    )


def lerp_hsv(
    c1: tuple[int, int, int],
    c2: tuple[int, int, int],
    t: float,
) -> tuple[int, int, int]:
    """Interpolate between two RGB colors through HSV space (better gradients)."""
    t = max(0.0, min(1.0, t))
    h1, s1, v1 = rgb_to_hsv(*c1)
    h2, s2, v2 = rgb_to_hsv(*c2)

    # Take the shorter path around the hue circle
    if abs(h2 - h1) > 180:
        if h1 < h2:
            h1 += 360
        else:
            h2 += 360

    h = lerp(h1, h2, t) % 360
    s = lerp(s1, s2, t)
    v = lerp(v1, v2, t)
    return hsv_to_rgb(h, s, v)


def dim_color(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    """Dim a color by a factor (0.0 = black, 1.0 = original)."""
    factor = max(0.0, min(1.0, factor))
    return (
        int(color[0] * factor),
        int(color[1] * factor),
        int(color[2] * factor),
    )


def apply_brightness(
    colors: dict[int, tuple[int, int, int]], brightness: int
) -> dict[int, tuple[int, int, int]]:
    """Apply a brightness level (0-100) to all colors."""
    if brightness >= 100:
        return colors
    factor = brightness / 100.0
    return {k: dim_color(v, factor) for k, v in colors.items()}


# --- Resolve theme color references ---

def resolve_color(
    color_ref: str, theme_colors: dict[str, tuple[int, int, int]]
) -> tuple[int, int, int]:
    """
    Resolve a color reference to an RGB tuple.

    color_ref can be:
    - A theme variable name like "accent" or "color1"
    - A hex color like "#ff0000"
    """
    if color_ref.startswith("#"):
        h = color_ref.lstrip("#")
        try:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        except (ValueError, IndexError):
            return (128, 128, 128)

    return theme_colors.get(color_ref, (128, 128, 128))


# --- Pattern implementations ---

def _get_layout_keycodes() -> list[int]:
    """Get all Linux keycodes from the physical layout."""
    codes = []
    for row in PHYSICAL_LAYOUT:
        for entry in row:
            if entry is not None:
                codes.append(entry[0])
    return codes


def pattern_solid(
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "color1",
    **kwargs,
) -> dict[int, tuple[int, int, int]]:
    """All keys set to the primary color."""
    color = resolve_color(primary, theme_colors)
    return {kc: color for kc in get_all_linux_keycodes()}


def pattern_gradient_h(
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "color1",
    **kwargs,
) -> dict[int, tuple[int, int, int]]:
    """Horizontal gradient from primary (left) to secondary (right)."""
    c1 = resolve_color(primary, theme_colors)
    c2 = resolve_color(secondary, theme_colors)
    result = {}
    for kc in get_all_linux_keycodes():
        pos = get_key_normalized_position(kc)
        if pos:
            result[kc] = lerp_hsv(c1, c2, pos[0])
        else:
            result[kc] = c1
    return result


def pattern_gradient_v(
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "color1",
    **kwargs,
) -> dict[int, tuple[int, int, int]]:
    """Vertical gradient from primary (top) to secondary (bottom)."""
    c1 = resolve_color(primary, theme_colors)
    c2 = resolve_color(secondary, theme_colors)
    result = {}
    for kc in get_all_linux_keycodes():
        pos = get_key_normalized_position(kc)
        if pos:
            result[kc] = lerp_hsv(c1, c2, pos[1])
        else:
            result[kc] = c1
    return result


def pattern_gradient_diag(
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "color1",
    **kwargs,
) -> dict[int, tuple[int, int, int]]:
    """Diagonal gradient from top-left to bottom-right."""
    c1 = resolve_color(primary, theme_colors)
    c2 = resolve_color(secondary, theme_colors)
    result = {}
    for kc in get_all_linux_keycodes():
        pos = get_key_normalized_position(kc)
        if pos:
            t = (pos[0] + pos[1]) / 2.0
            result[kc] = lerp_hsv(c1, c2, t)
        else:
            result[kc] = c1
    return result


def pattern_zones(
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "color1",
    **kwargs,
) -> dict[int, tuple[int, int, int]]:
    """Color keys by functional zone."""
    accent = resolve_color("accent", theme_colors)
    c1 = resolve_color("color1", theme_colors)
    c2 = resolve_color("color2", theme_colors)
    c4 = resolve_color("color4", theme_colors)
    c5 = resolve_color("color5", theme_colors)
    fg = resolve_color("foreground", theme_colors)

    result = {}

    # Default: foreground dimmed
    for kc in get_all_linux_keycodes():
        result[kc] = dim_color(fg, 0.3)

    # F-row in color1
    for kc in KEY_ALIASES["f_row"]:
        result[kc] = c1

    # Letters in accent
    for kc in KEY_ALIASES["letters"]:
        result[kc] = accent

    # Modifiers in color5
    for kc in KEY_ALIASES["modifiers"]:
        result[kc] = c5

    # Arrows in color2
    for kc in KEY_ALIASES["arrows"]:
        result[kc] = c2

    # Number row in color4
    for kc in KEY_ALIASES["num_row"]:
        result[kc] = c4

    # WASD highlighted
    for kc in KEY_ALIASES["wasd"]:
        result[kc] = c2

    # Numpad
    for kc in KEY_ALIASES["numpad"]:
        result[kc] = dim_color(c4, 0.6)

    # Special keys
    result[9] = c1   # Esc
    result[65] = accent  # Space

    return result


def pattern_accent_keys(
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "background",
    **kwargs,
) -> dict[int, tuple[int, int, int]]:
    """Most keys dim background, important keys in accent."""
    accent = resolve_color(primary, theme_colors)
    bg = resolve_color(secondary, theme_colors)
    dim_bg = dim_color(bg, 0.4) if bg != (0, 0, 0) else (15, 15, 15)

    result = {}
    for kc in get_all_linux_keycodes():
        result[kc] = dim_bg

    # Highlighted keys
    highlight_keys = (
        KEY_ALIASES["wasd"]
        + KEY_ALIASES["arrows"]
        + [9, 36, 65, 22]  # Esc, Enter, Space, Backspace
    )
    for kc in highlight_keys:
        result[kc] = accent

    return result


def pattern_scatter(
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "color1",
    **kwargs,
) -> dict[int, tuple[int, int, int]]:
    """Distribute theme colors across keys using a deterministic hash."""
    # Use all 16 terminal colors
    palette = [
        resolve_color(f"color{i}", theme_colors) for i in range(16)
    ]
    # Add accent for extra emphasis
    palette.append(resolve_color("accent", theme_colors))

    result = {}
    for kc in get_all_linux_keycodes():
        # Deterministic hash based on keycode
        h = hashlib.md5(f"scatter-{kc}".encode()).hexdigest()
        idx = int(h[:8], 16) % len(palette)
        result[kc] = palette[idx]
    return result


def pattern_split_h(
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "color1",
    **kwargs,
) -> dict[int, tuple[int, int, int]]:
    """Left half primary, right half secondary."""
    c1 = resolve_color(primary, theme_colors)
    c2 = resolve_color(secondary, theme_colors)
    result = {}
    for kc in get_all_linux_keycodes():
        pos = get_key_normalized_position(kc)
        if pos and pos[0] > 0.5:
            result[kc] = c2
        else:
            result[kc] = c1
    return result


def pattern_split_v(
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "color1",
    **kwargs,
) -> dict[int, tuple[int, int, int]]:
    """Top half primary, bottom half secondary."""
    c1 = resolve_color(primary, theme_colors)
    c2 = resolve_color(secondary, theme_colors)
    result = {}
    for kc in get_all_linux_keycodes():
        pos = get_key_normalized_position(kc)
        if pos and pos[1] > 0.5:
            result[kc] = c2
        else:
            result[kc] = c1
    return result


def pattern_rainbow(
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "color1",
    **kwargs,
) -> dict[int, tuple[int, int, int]]:
    """Cycle through all 16 theme colors across columns."""
    palette = [
        resolve_color(f"color{i}", theme_colors) for i in range(16)
    ]
    result = {}
    for kc in get_all_linux_keycodes():
        pos = get_key_normalized_position(kc)
        if pos:
            idx = int(pos[0] * (len(palette) - 1))
            result[kc] = palette[idx]
        else:
            result[kc] = palette[0]
    return result


def pattern_wave(
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "color1",
    **kwargs,
) -> dict[int, tuple[int, int, int]]:
    """Sine wave gradient across the keyboard."""
    c1 = resolve_color(primary, theme_colors)
    c2 = resolve_color(secondary, theme_colors)
    result = {}
    for kc in get_all_linux_keycodes():
        pos = get_key_normalized_position(kc)
        if pos:
            # Sine wave: 1.5 full cycles across the keyboard
            t = (math.sin(pos[0] * math.pi * 3) + 1) / 2.0
            result[kc] = lerp_hsv(c1, c2, t)
        else:
            result[kc] = c1
    return result


def pattern_ripple(
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "color1",
    **kwargs,
) -> dict[int, tuple[int, int, int]]:
    """Concentric ripple from center of keyboard."""
    c1 = resolve_color(primary, theme_colors)
    c2 = resolve_color(secondary, theme_colors)
    result = {}
    # Center of keyboard
    cx, cy = 0.5, 0.5
    for kc in get_all_linux_keycodes():
        pos = get_key_normalized_position(kc)
        if pos:
            dist = math.sqrt((pos[0] - cx) ** 2 + (pos[1] - cy) ** 2)
            # 2 ripple rings
            t = (math.sin(dist * math.pi * 4) + 1) / 2.0
            result[kc] = lerp_hsv(c1, c2, t)
        else:
            result[kc] = c1
    return result


def pattern_border(
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "background",
    **kwargs,
) -> dict[int, tuple[int, int, int]]:
    """Accent color on edge keys, secondary in the middle."""
    c1 = resolve_color(primary, theme_colors)
    c2 = resolve_color(secondary, theme_colors)
    c2 = dim_color(c2, 0.4) if c2 != (0, 0, 0) else (15, 15, 15)
    result = {}
    for kc in get_all_linux_keycodes():
        pos = get_key_normalized_position(kc)
        if pos:
            # Edge detection: close to any border
            edge_dist = min(pos[0], 1.0 - pos[0], pos[1], 1.0 - pos[1])
            if edge_dist < 0.15:
                result[kc] = c1
            else:
                result[kc] = c2
        else:
            result[kc] = c2
    return result


# --- Pattern registry ---

KEYBOARD_PATTERNS: dict[str, Callable] = {
    "solid": pattern_solid,
    "gradient-h": pattern_gradient_h,
    "gradient-v": pattern_gradient_v,
    "gradient-diag": pattern_gradient_diag,
    "zones": pattern_zones,
    "accent-keys": pattern_accent_keys,
    "scatter": pattern_scatter,
    "split-h": pattern_split_h,
    "split-v": pattern_split_v,
    "rainbow": pattern_rainbow,
    "wave": pattern_wave,
    "ripple": pattern_ripple,
    "border": pattern_border,
}

KEYBOARD_PATTERN_DESCRIPTIONS: dict[str, str] = {
    "solid": "All keys one color",
    "gradient-h": "Left-to-right gradient",
    "gradient-v": "Top-to-bottom gradient",
    "gradient-diag": "Diagonal gradient",
    "zones": "Color by key function",
    "accent-keys": "Highlight WASD/arrows/etc",
    "scatter": "Distributed theme colors",
    "split-h": "Left/right split",
    "split-v": "Top/bottom split",
    "rainbow": "All 16 theme colors across columns",
    "wave": "Sine wave gradient",
    "ripple": "Concentric rings from center",
    "border": "Accent border, dim center",
}

LIGHTBAR_PATTERNS: dict[str, str] = {
    "solid": "Single color",
    "accent": "Theme accent color",
    "primary": "Same as keyboard primary",
}


def generate_keyboard_colors(
    pattern: str,
    theme_colors: dict[str, tuple[int, int, int]],
    primary: str = "accent",
    secondary: str = "color1",
    brightness: int = 100,
) -> dict[int, tuple[int, int, int]]:
    """
    Generate a per-key color map for the keyboard.

    Args:
        pattern: Pattern name from KEYBOARD_PATTERNS
        theme_colors: Dict of theme color name -> RGB tuple
        primary: Theme color variable for primary color
        secondary: Theme color variable for secondary color
        brightness: Brightness level 0-100

    Returns:
        Dict mapping MSI keycode -> (R, G, B) tuple
    """
    pattern_fn = KEYBOARD_PATTERNS.get(pattern, pattern_solid)
    linux_colors = pattern_fn(
        theme_colors, primary=primary, secondary=secondary
    )

    # Apply brightness
    if brightness < 100:
        linux_colors = apply_brightness(linux_colors, brightness)

    # Convert Linux keycodes to MSI keycodes
    msi_colors = {}
    for linux_kc, color in linux_colors.items():
        if linux_kc == -1:
            msi_colors[FN_MSI_KEYCODE] = color
        else:
            msi_kc = LINUX_TO_MSI.get(linux_kc)
            if msi_kc is not None:
                msi_colors[msi_kc] = color

    return msi_colors


def generate_lightbar_color(
    pattern: str,
    theme_colors: dict[str, tuple[int, int, int]],
    color_ref: str = "accent",
    brightness: int = 100,
) -> tuple[int, int, int]:
    """
    Generate a color for the light bar.

    Currently only supports solid colors (per-LED bar control
    requires further reverse engineering).
    """
    if pattern == "accent":
        color = resolve_color("accent", theme_colors)
    elif pattern == "primary":
        color = resolve_color(color_ref, theme_colors)
    else:
        color = resolve_color(color_ref, theme_colors)

    if brightness < 100:
        color = dim_color(color, brightness / 100.0)

    return color
