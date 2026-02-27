# omarchy-msi-rgb

Theme-reactive per-key RGB control for MSI Raider laptops with SteelSeries controllers, integrated with [Omarchy](https://omarchy.org/).

When you change your Omarchy theme, your keyboard and light bar colors change with it.

## Supported Hardware

- **MSI Raider GE68 HX** (confirmed: 13VG and similar)
- Other MSI laptops with SteelSeries KLC/ALC controllers (`1038:113a` / `1038:114b`) should also work

### RGB Zones

| Zone | USB Device | Status |
|------|-----------|--------|
| Per-key keyboard | SteelSeries KLC (`1038:113a`) | Full per-key control |
| Front light bar | SteelSeries ALC (`1038:114b`) | Solid color (per-LED TBD) |
| Dragon logo (lid) | Likely part of ALC | Needs testing |

## Installation

### From AUR (recommended)

```bash
yay -S omarchy-msi-rgb
```

### Manual

```bash
git clone https://github.com/cld3d/omarchy-msi-rgb.git
cd omarchy-msi-rgb
sudo make install
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Dependencies

- `python` (3.12+)
- `hidapi` (USB HID communication)

## Usage

### Apply RGB

```bash
omarchy-msi-rgb-apply
```

Reads the current Omarchy theme colors and applies them to the keyboard and light bar. Colors are always derived from the theme automatically:

- **Keyboard primary** = `accent`
- **Keyboard secondary** = `color1`
- **Light bar** = `accent`

### Auto-apply on Theme Change

Set up the Omarchy theme hook:

```bash
cp /usr/share/omarchy-msi-rgb/hooks/theme-set.sample ~/.config/omarchy/hooks/theme-set
chmod +x ~/.config/omarchy/hooks/theme-set
```

Now every `omarchy-theme-set <theme>` will automatically update your RGB.

## Keyboard Patterns

| Pattern | Description |
|---------|------------|
| `solid` | All keys one color |
| `gradient-h` | Left-to-right gradient between two theme colors |
| `gradient-v` | Top-to-bottom gradient |
| `gradient-diag` | Diagonal gradient |
| `zones` | Color by key function (F-keys, letters, modifiers, arrows, numpad) |
| `accent-keys` | Highlight WASD, arrows, enter; dim everything else |
| `scatter` | Distribute all 16 theme colors across keys |
| `split-h` | Left half / right half split |
| `split-v` | Top half / bottom half split |
| `rainbow` | All 16 theme colors spread across columns |
| `wave` | Sine wave gradient |
| `ripple` | Concentric rings from keyboard center |
| `border` | Accent color on edge keys, dim center |

## Configuration

Optionally create `~/.config/omarchy/msi-rgb.toml` to change pattern or brightness:

```toml
[keyboard]
pattern = "gradient-h"
brightness = 100

[lightbar]
brightness = 100
```

Colors are not configurable — they always come from the active Omarchy theme.

## How It Works

1. Reads colors from `~/.config/omarchy/current/theme/colors.toml`
2. Pattern engine generates per-key RGB values based on each key's physical position
3. Colors are sent to the SteelSeries controllers via HID feature reports through `libhidapi`
4. The Omarchy `theme-set` hook triggers this automatically on theme changes

### Protocol

Based on the reverse-engineering work of [msi-perkeyrgb](https://github.com/Askannz/msi-perkeyrgb). The keyboard is divided into 4 regions (alphanum, enter, modifiers, numpad), each addressed via 524-byte HID feature reports containing per-key RGB data. A 64-byte refresh packet commits the changes.

## Troubleshooting

**"Cannot open HID device"** — Check udev rules are installed and active:
```bash
ls -la /dev/hidraw*
```
Try rebooting after installing udev rules. Your user must be in the `input` group.

**Device not detected** — Verify your laptop has the SteelSeries controllers:
```bash
cat /sys/bus/usb/devices/*/idVendor  # look for 1038
```

**Wrong key colors** — The GE63 keymap is used by default. If some keys show the wrong color, the keymap may need adjustment for your specific model. Open an issue.

## Contributing

PRs welcome, especially for:
- Per-LED light bar control (requires USB protocol capture from Windows/MSI Center)
- Dragon logo control
- Additional MSI laptop model keymaps
- New patterns

## Credits

- Protocol based on [msi-perkeyrgb](https://github.com/Askannz/msi-perkeyrgb) by Askannz
- GE68 HX compatibility confirmed by [issue #63](https://github.com/Askannz/msi-perkeyrgb/issues/63)
- Built for [Omarchy](https://omarchy.org/)

## License

MIT
