"""
HID protocol for MSI SteelSeries RGB controllers.

Communicates with the SteelSeries KLC (Keyboard Light Controller) and
ALC (Auxiliary Light Controller) embedded in MSI Raider laptops via
the hidapi C library loaded through ctypes.

Protocol reverse-engineered by the msi-perkeyrgb project:
https://github.com/Askannz/msi-perkeyrgb
"""

import ctypes
import ctypes.util
import os
from pathlib import Path
import subprocess
import sys
from time import sleep

# --- Constants ---

# USB Vendor/Product IDs for GE68 HX SteelSeries controllers
STEELSERIES_VID = 0x1038
KLC_PID = 0x113A  # Keyboard per-key RGB
ALC_PID = 0x114B  # Light bar / ambient

# Protocol constants
NB_KEYS_PER_REGION = 42
INTER_COMMAND_DELAY = 0.01  # 10ms between HID commands
KEY_FRAGMENT_SIZE = 12

# Region IDs in the wire protocol
REGION_IDS = {
    "alphanum": 0x2A,
    "enter": 0x0B,
    "modifiers": 0x18,
    "numpad": 0x24,
}

# MSI keycodes belonging to each region (42 slots each, 0x00 = unused)
REGION_KEYCODES = {
    "alphanum": [
        4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
        20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
        35, 36, 37, 38, 39, 58, 59, 60, 61, 62, 63,
    ],
    "enter": [
        40, 49, 50, 100, 135, 136, 137, 138, 139, 144, 145,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ],
    "modifiers": [
        41, 42, 43, 44, 45, 46, 47, 48, 51, 52, 53, 54, 55, 56, 57,
        101, 224, 225, 226, 227, 228, 229, 230, 240,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ],
    "numpad": [
        64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78,
        79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93,
        94, 95, 96, 97, 98, 99,
        0, 0, 0, 0, 0, 0,
    ],
}

# Reverse lookup: MSI keycode -> region name
_MSI_KEYCODE_TO_REGION = {}
for _region, _codes in REGION_KEYCODES.items():
    for _code in _codes:
        if _code != 0:
            _MSI_KEYCODE_TO_REGION[_code] = _region


# --- HIDAPI ctypes wrapper ---

class HIDAPIError(Exception):
    """Error communicating with HID device."""


def _find_hidapi_lib():
    """Locate the hidapi-hidraw shared library."""
    # Try direct name first (common on Arch Linux)
    for name in ("libhidapi-hidraw.so", "libhidapi-hidraw.so.0"):
        try:
            return ctypes.cdll.LoadLibrary(name)
        except OSError:
            continue

    # Try ctypes.util finder
    path = ctypes.util.find_library("hidapi-hidraw")
    if path:
        try:
            return ctypes.cdll.LoadLibrary(path)
        except OSError:
            pass

    # Try generic hidapi as fallback
    path = ctypes.util.find_library("hidapi")
    if path:
        try:
            return ctypes.cdll.LoadLibrary(path)
        except OSError:
            pass

    return None


class HIDDevice:
    """Low-level wrapper around a single HID device via hidapi."""

    _lib = None
    _initialized = False

    @classmethod
    def _ensure_lib(cls):
        if cls._lib is not None:
            return
        cls._lib = _find_hidapi_lib()
        if cls._lib is None:
            raise HIDAPIError(
                "Could not load libhidapi-hidraw. "
                "Install hidapi: sudo pacman -S hidapi"
            )
        if not cls._initialized:
            cls._lib.hid_init()
            cls._initialized = True

    def __init__(self, vid: int, pid: int):
        self._ensure_lib()
        self._vid = vid
        self._pid = pid
        self._device = None

    def open(self):
        """Open the HID device. Raises HIDAPIError on failure."""
        self._device = self._lib.hid_open(self._vid, self._pid, None)
        if not self._device:
            raise HIDAPIError(
                f"Cannot open HID device {self._vid:04x}:{self._pid:04x}. "
                f"Check udev rules and device connection."
            )

    def close(self):
        """Close the HID device."""
        if self._device:
            self._lib.hid_close(self._device)
            self._device = None

    def send_feature_report(self, data: bytes):
        """Send a feature report (used for color data packets)."""
        if not self._device:
            raise HIDAPIError("Device not open")
        buf = ctypes.create_string_buffer(data)
        ret = self._lib.hid_send_feature_report(self._device, buf, len(data))
        if ret < 0:
            raise HIDAPIError(f"hid_send_feature_report failed (returned {ret})")
        sleep(INTER_COMMAND_DELAY)

    def send_output_report(self, data: bytes):
        """Send an output report (used for refresh command)."""
        if not self._device:
            raise HIDAPIError("Device not open")
        buf = ctypes.create_string_buffer(data)
        ret = self._lib.hid_write(self._device, buf, len(data))
        if ret < 0:
            raise HIDAPIError(f"hid_write failed (returned {ret})")
        sleep(INTER_COMMAND_DELAY)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()


# --- Packet construction ---

def build_color_packet(region: str, keycode_colors: dict[int, tuple[int, int, int]]) -> bytes:
    """
    Build a 524-byte color packet for a keyboard region.

    Args:
        region: One of "alphanum", "enter", "modifiers", "numpad"
        keycode_colors: dict mapping MSI keycode -> (R, G, B) tuple

    Returns:
        bytes: The complete feature report packet
    """
    region_id = REGION_IDS[region]
    packet = [0x0E, 0x00, region_id, 0x00]  # 4-byte header

    keys_written = 0
    for keycode, (r, g, b) in keycode_colors.items():
        fragment = [
            r & 0xFF, g & 0xFF, b & 0xFF,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x01, 0x00,
            keycode & 0xFF,
        ]
        packet.extend(fragment)
        keys_written += 1

    # Pad remaining key slots with zeros
    while keys_written < NB_KEYS_PER_REGION:
        packet.extend([0x00] * KEY_FRAGMENT_SIZE)
        keys_written += 1

    # 16-byte footer
    footer = [0x00] * 14 + [0x08, 0x39]
    packet.extend(footer)

    return bytes(packet)


def build_refresh_packet() -> bytes:
    """Build the 64-byte refresh packet that commits color changes."""
    return bytes([0x09] + [0x00] * 63)


# --- High-level device controllers ---

def _check_device_exists(vid: int, pid: int) -> bool:
    """Check if a USB device with the given VID:PID exists via sysfs."""
    vid_hex = f"{vid:04x}"
    pid_hex = f"{pid:04x}"
    try:
        usb_devices = Path("/sys/bus/usb/devices")
        if not usb_devices.exists():
            return False
        for device_dir in usb_devices.iterdir():
            try:
                dev_vid = (device_dir / "idVendor").read_text().strip()
                dev_pid = (device_dir / "idProduct").read_text().strip()
                if dev_vid == vid_hex and dev_pid == pid_hex:
                    return True
            except (IOError, OSError):
                continue
        return False
    except (IOError, OSError):
        return False


class KeyboardRGB:
    """Control the per-key RGB keyboard (SteelSeries KLC)."""

    def __init__(self, vid: int = STEELSERIES_VID, pid: int = KLC_PID):
        self.vid = vid
        self.pid = pid

    def is_available(self) -> bool:
        """Check if the keyboard RGB device is present."""
        return _check_device_exists(self.vid, self.pid)

    def set_per_key(self, msi_colors: dict[int, tuple[int, int, int]]):
        """
        Set per-key colors on the keyboard.

        Args:
            msi_colors: dict mapping MSI keycode -> (R, G, B)
        """
        # Group colors by region
        region_colors: dict[str, dict[int, tuple[int, int, int]]] = {
            r: {} for r in REGION_IDS
        }

        for msi_keycode, color in msi_colors.items():
            region = _MSI_KEYCODE_TO_REGION.get(msi_keycode)
            if region:
                region_colors[region][msi_keycode] = color

        with HIDDevice(self.vid, self.pid) as dev:
            for region_name in REGION_IDS:
                colors = region_colors[region_name]
                if colors:
                    packet = build_color_packet(region_name, colors)
                    dev.send_feature_report(packet)
            dev.send_output_report(build_refresh_packet())

    def set_all(self, r: int, g: int, b: int):
        """Set all keys to a single color."""
        all_colors = {}
        for region_codes in REGION_KEYCODES.values():
            for keycode in region_codes:
                if keycode != 0:
                    all_colors[keycode] = (r, g, b)
        self.set_per_key(all_colors)


class LightbarRGB:
    """Control the light bar / ambient LEDs (SteelSeries ALC)."""

    def __init__(self, vid: int = STEELSERIES_VID, pid: int = ALC_PID):
        self.vid = vid
        self.pid = pid

    def is_available(self) -> bool:
        """Check if the light bar device is present."""
        return _check_device_exists(self.vid, self.pid)

    def set_all(self, r: int, g: int, b: int):
        """
        Set the entire light bar to a single color.

        Uses the same protocol as the keyboard (set_color_all equivalent
        from msi-perkeyrgb), which has been confirmed working on GE68 HX.
        """
        all_colors = {}
        for region_codes in REGION_KEYCODES.values():
            for keycode in region_codes:
                if keycode != 0:
                    all_colors[keycode] = (r, g, b)

        region_grouped: dict[str, dict[int, tuple[int, int, int]]] = {
            rname: {} for rname in REGION_IDS
        }
        for msi_keycode, color in all_colors.items():
            region = _MSI_KEYCODE_TO_REGION.get(msi_keycode)
            if region:
                region_grouped[region][msi_keycode] = color

        with HIDDevice(self.vid, self.pid) as dev:
            for region_name in REGION_IDS:
                colors = region_grouped[region_name]
                if colors:
                    packet = build_color_packet(region_name, colors)
                    dev.send_feature_report(packet)
            dev.send_output_report(build_refresh_packet())
