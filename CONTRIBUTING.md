# Contributing to Cursor Concept

Thank you for your interest in contributing to **Cursor Concept**! This project aims to maintain the highest standard of Windows mouse pointer aesthetics, performance, and stability.

---

## Development Setup

1. **Prerequisites**:
   - Windows 10 or Windows 11 (64 bit)
   - Python 3.10 or later
2. **Clone & Install Dependencies**:
   ```powershell
   git clone https://github.com/EminenceShade/Cursor-Concept.git
   cd Cursor-Concept/Data
   pip install pywebview pillow numpy
   ```
3. **Run in Development Mode**:
   ```powershell
   python main.py
   ```

---

## Design Heritage & Vector Attribution

All cursor shapes and transformation designs in Cursor Concept are based on the original *Windows 11 Cursor Concept* by **jepriCreations** ([jepricreations.com](https://jepricreations.com/)). Contributions extending the cursor catalog should preserve this distinct aesthetic geometry.

---

## Submitting Custom Presets or Transformations

We welcome community crafted color presets and authentic cursor transformations.

### Guidelines for Presets:
- Must specify a unique, evocative name.
- Color combinations should maintain high contrast against both dark and light backgrounds.
- Provide tested Hex stops and outline colors in `Data/ui/app.js`.


### Guidelines for Vector Cursor Models:
- All cursors must strictly follow standard Windows hotspot rules (e.g. `(8, 4)` for top left pointer tips, `(15, 15)` for centered crosshairs and 4 way move).
- No arbitrary AI generated shapes that distort standard cursor affordances.
- Include multi resolution assets `[32x32, 48x48, 64x64, 96x96]` for Ultra HDPI display scaling.

---

## Pull Request Workflow

1. Fork the repository and create a feature branch (`git checkout -b feature/awesome-preset`).
2. Verify that `python main.py` launches cleanly with zero console warnings.
3. Test **Apply to Windows**, **Revert Default**, and **Export Pack** to ensure Win32 registry calls succeed.
4. Commit your changes with clear, descriptive messages.
5. Open a Pull Request with before/after screenshots of your changes.

