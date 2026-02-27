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
- `python-textual` (TUI framework)
- `python-tomlkit` (config parsing)
- `hidapi` (USB HID communication)

## Usage

### TUI Configurator

```bash
omarchy-msi-rgb
```

Opens an interactive terminal UI where you can:
- Preview and select keyboard patterns
- Choose which theme colors to use as primary/secondary
- Pick light bar colors
- Apply changes live to hardware
- Save configuration

### Headless Apply

```bash
omarchy-msi-rgb-apply
```

Reads the saved configuration and applies it using the current theme's colors. Designed to be called from hooks.

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

Saved at `~/.config/omarchy/msi-rgb.toml`:

```toml
[keyboard]
pattern = "gradient-h"
primary = "accent"
secondary = "color1"
brightness = 100

[lightbar]
pattern = "solid"
color = "accent"
brightness = 100
```

Color values reference Omarchy theme variables: `accent`, `foreground`, `background`, `color0`-`color15`, etc.

## How It Works

1. Reads colors from `~/.config/omarchy/current/theme/colors.toml`
2. Pattern engine generates per-key RGB values based on each key's physical position
3. Colors are sent to the SteelSeries controllers via HID feature reports through `libhidapi`
4. The Omarchy `theme-set` hook triggers this automatically on theme changes

### Protocol

Based on the reverse-engineering work of [msi-perkeyrgb](https://github.com/Askannz/msi-perkeyrgb). The keyboard is divided into 4 regions (alphanum, enter, modifiers, numpad), each addressed via 524-byte HID feature reports containing per-key RGB data. A 64-byte refresh packet commits the changes.

## Troubleshooting

**"Cannot open HID device"** - Check udev rules are installed and active:
```bash
ls -la /dev/hidraw*          # Should show group-readable devices
lsusb | grep 1038            # Should show KLC and ALC
```
Try rebooting after installing udev rules.

**Device not detected** - Verify your laptop has the SteelSeries controllers:
```bash
lsusb | grep -i steelseries
```

**Wrong key colors** - The GE63 keymap is used by default. If some keys show the wrong color, the keymap may need adjustment for your specific model. Open an issue.

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
