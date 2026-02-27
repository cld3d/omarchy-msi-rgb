"""
Keyboard layout and keycode mapping for MSI Raider GE68 HX.

Maps between three coordinate systems:
1. Physical position (row, col) - where the key is on the keyboard
2. Linux/X11 keycode - what the OS calls the key
3. MSI keycode - what the SteelSeries controller calls the key

The physical layout is used by the pattern engine for spatial effects
(gradients, waves, zones, etc.).
"""

# Linux X11 keycode -> MSI internal keycode (GE63 keymap from msi-perkeyrgb)
LINUX_TO_MSI: dict[int, int] = {
    9: 41,     # Esc
    10: 30,    # 1
    11: 31,    # 2
    12: 32,    # 3
    13: 33,    # 4
    14: 34,    # 5
    15: 35,    # 6
    16: 36,    # 7
    17: 37,    # 8
    18: 38,    # 9
    19: 39,    # 0
    20: 45,    # -
    21: 46,    # =
    22: 42,    # Backspace
    23: 43,    # Tab
    24: 20,    # Q
    25: 26,    # W
    26: 8,     # E
    27: 21,    # R
    28: 23,    # T
    29: 28,    # Y
    30: 24,    # U
    31: 12,    # I
    32: 18,    # O
    33: 19,    # P
    34: 47,    # [
    35: 48,    # ]
    36: 40,    # Enter
    37: 224,   # LCtrl
    38: 4,     # A
    39: 22,    # S
    40: 7,     # D
    41: 9,     # F
    42: 10,    # G
    43: 11,    # H
    44: 13,    # J
    45: 14,    # K
    46: 15,    # L
    47: 51,    # ;
    48: 52,    # '
    49: 53,    # `
    50: 225,   # LShift
    51: 49,    # backslash
    52: 29,    # Z
    53: 27,    # X
    54: 6,     # C
    55: 25,    # V
    56: 5,     # B
    57: 17,    # N
    58: 16,    # M
    59: 54,    # ,
    60: 55,    # .
    61: 56,    # /
    62: 229,   # RShift
    63: 85,    # KP *
    64: 226,   # LAlt
    65: 44,    # Space
    66: 57,    # CapsLock
    67: 58,    # F1
    68: 59,    # F2
    69: 60,    # F3
    70: 61,    # F4
    71: 62,    # F5
    72: 63,    # F6
    73: 64,    # F7  (actually MSI keycode for numpad, but matches GE63 map)
    74: 65,    # F8
    75: 66,    # F9
    76: 67,    # F10
    77: 83,    # NumLock
    78: 71,    # ScrollLock
    79: 95,    # KP 7
    80: 96,    # KP 8
    81: 97,    # KP 9
    82: 86,    # KP -
    83: 92,    # KP 4
    84: 93,    # KP 5
    85: 94,    # KP 6
    86: 87,    # KP +
    87: 89,    # KP 1
    88: 90,    # KP 2
    89: 91,    # KP 3
    90: 98,    # KP 0
    91: 99,    # KP .
    94: 100,   # < (ISO key)
    95: 68,    # F11
    96: 69,    # F12
    104: 88,   # KP Enter
    105: 228,  # RCtrl
    106: 84,   # KP /
    107: 70,   # PrtSc
    108: 230,  # RAlt
    111: 82,   # Up
    112: 75,   # PgUp
    113: 80,   # Left
    114: 79,   # Right
    116: 81,   # Down
    117: 78,   # PgDn
    118: 73,   # Insert
    119: 76,   # Delete
    127: 72,   # Pause
    133: 227,  # Super (Win)
}

# Special key alias
FN_MSI_KEYCODE = 240

# Physical keyboard layout as a 2D grid.
# Each entry is a (linux_keycode, label, width) tuple.
# Width is in units (1 = standard key width, 1.5 = 1.5x wide, etc.)
# None entries are empty spaces.
# This represents the GE68 HX ANSI layout (no numpad shown for TUI simplicity,
# but numpad keys are still controllable via patterns).

PHYSICAL_LAYOUT: list[list[tuple[int, str, float] | None]] = [
    # Row 0: Escape + F-keys
    [
        (9, "Esc", 1), None,
        (67, "F1", 1), (68, "F2", 1), (69, "F3", 1), (70, "F4", 1), None,
        (71, "F5", 1), (72, "F6", 1), (73, "F7", 1), (74, "F8", 1), None,
        (75, "F9", 1), (76, "F10", 1), (95, "F11", 1), (96, "F12", 1),
        None,
        (119, "Del", 1),
    ],
    # Row 1: Number row
    [
        (49, "`", 1), (10, "1", 1), (11, "2", 1), (12, "3", 1),
        (13, "4", 1), (14, "5", 1), (15, "6", 1), (16, "7", 1),
        (17, "8", 1), (18, "9", 1), (19, "0", 1), (20, "-", 1),
        (21, "=", 1), (22, "Bksp", 2),
        None,
        (118, "Ins", 1),
    ],
    # Row 2: QWERTY row
    [
        (23, "Tab", 1.5), (24, "Q", 1), (25, "W", 1), (26, "E", 1),
        (27, "R", 1), (28, "T", 1), (29, "Y", 1), (30, "U", 1),
        (31, "I", 1), (32, "O", 1), (33, "P", 1), (34, "[", 1),
        (35, "]", 1), (51, "\\", 1.5),
        None,
        (112, "PgU", 1),
    ],
    # Row 3: Home row
    [
        (66, "Caps", 1.75), (38, "A", 1), (39, "S", 1), (40, "D", 1),
        (41, "F", 1), (42, "G", 1), (43, "H", 1), (44, "J", 1),
        (45, "K", 1), (46, "L", 1), (47, ";", 1), (48, "'", 1),
        (36, "Enter", 2.25),
        None,
        (117, "PgD", 1),
    ],
    # Row 4: Shift row
    [
        (50, "Shift", 2.25), (52, "Z", 1), (53, "X", 1), (54, "C", 1),
        (55, "V", 1), (56, "B", 1), (57, "N", 1), (58, "M", 1),
        (59, ",", 1), (60, ".", 1), (61, "/", 1),
        (62, "Shift", 1.75),
        None,
        (111, "Up", 1),
        None,
    ],
    # Row 5: Bottom row
    [
        (37, "Ctrl", 1.25), (-1, "Fn", 1), (133, "Win", 1.25),
        (64, "Alt", 1.25), (65, "Space", 5.75),
        (108, "Alt", 1.25), (105, "Ctrl", 1.25),
        None,
        (113, "Lt", 1), (116, "Dn", 1), (114, "Rt", 1),
    ],
]

# Key aliases for pattern configuration (sets of Linux keycodes)
KEY_ALIASES: dict[str, list[int]] = {
    "all": [k for k in LINUX_TO_MSI.keys()] + [-1],  # -1 = Fn
    "f_row": [67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 95, 96],
    "arrows": [111, 113, 114, 116],
    "wasd": [25, 38, 39, 40],
    "num_row": list(range(10, 22)),
    "modifiers": [37, 50, 64, 66, 105, 108, 62, 133, -1],
    "letters": [
        24, 25, 26, 27, 28, 29, 30, 31, 32, 33,  # Q-P
        38, 39, 40, 41, 42, 43, 44, 45, 46,       # A-L
        52, 53, 54, 55, 56, 57, 58,                # Z-M
    ],
    "numpad": [79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 104, 106],
}

# Display labels for Linux keycodes
KEY_LABELS: dict[int, str] = {}
for _row in PHYSICAL_LAYOUT:
    for _entry in _row:
        if _entry is not None:
            _kc, _label, _w = _entry
            KEY_LABELS[_kc] = _label


def linux_to_msi(linux_keycode: int) -> int | None:
    """Convert a Linux X11 keycode to MSI internal keycode."""
    if linux_keycode == -1:
        return FN_MSI_KEYCODE
    return LINUX_TO_MSI.get(linux_keycode)


def get_key_position(linux_keycode: int) -> tuple[int, int] | None:
    """
    Get the (row, col_index) position of a key in the physical layout.
    col_index is the index within the row's key list (not accounting for widths).
    Returns None if the key is not in the layout.
    """
    for row_idx, row in enumerate(PHYSICAL_LAYOUT):
        col_idx = 0
        for entry in row:
            if entry is not None:
                kc, _, _ = entry
                if kc == linux_keycode:
                    return (row_idx, col_idx)
                col_idx += 1
            else:
                col_idx += 1
    return None


def get_key_normalized_position(linux_keycode: int) -> tuple[float, float] | None:
    """
    Get the normalized (x, y) position of a key, where both x and y
    are in the range [0.0, 1.0].

    x=0 is leftmost, x=1 is rightmost.
    y=0 is top row, y=1 is bottom row.

    This accounts for key widths to give accurate horizontal positions.
    """
    for row_idx, row in enumerate(PHYSICAL_LAYOUT):
        x_pos = 0.0
        for entry in row:
            if entry is None:
                x_pos += 0.5  # gap
                continue
            kc, _, width = entry
            key_center_x = x_pos + width / 2.0
            if kc == linux_keycode:
                # Normalize: max row width is approximately 17 units
                max_row_width = 17.0
                num_rows = len(PHYSICAL_LAYOUT)
                return (
                    min(1.0, key_center_x / max_row_width),
                    row_idx / max(1, num_rows - 1),
                )
            x_pos += width
    return None


def get_all_linux_keycodes() -> list[int]:
    """Get all Linux keycodes that have MSI keycode mappings."""
    return list(LINUX_TO_MSI.keys()) + [-1]
