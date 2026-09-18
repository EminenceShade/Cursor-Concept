# Cursor Concept: Technical Specification & Architecture Document

This document details the complete design, user experience (UI/UX), backend engine, frontend-backend integration, and Quality of Life (QoL) features for the **Cursor Concept** standalone desktop application (`Cursor Concept.exe`).

---

## 1. Design System & UI/UX Palette

The application is styled with an **Obsidian Glassmorphism** aesthetic inspired by modern creative design software (Figma, Raycast, and Linear). It provides high visual contrast, intuitive feedback, and clean, clutter free layouts.

### Color Palette

| Token | Hex Value | Role & Usage |
| :--- | :--- | :--- |
| **Canvas Background** | `#0b0d14` | Deep obsidian backdrop |
| **Surface Panel** | `#121520` | Sidebar and tray container background |
| **Card / Tray Surface** | `#1a1e2e` | Individual cursor cards and control cards |
| **Card Hover** | `#22273d` | Micro interaction hover feedback |
| **Glass Backdrop** | `#161a29cc` | Semi-transparent floating bars with `backdrop-filter: blur(16px)` |
| **Border Subtle** | `#272d42` | Default component borders |
| **Border Active** | `#a6a3ff88` | Active input or selected cursor highlight |
| **Primary Accent** | `#a6a3ff` | Moga Purple, primary action buttons, focused sliders |
| **Chroma Cyan** | `#00f0ff` | Secondary gradient accent & live status glow |
| **Chroma Pink** | `#ff2a85` | Gradient endpoint & badge indicators |
| **Success Emerald** | `#00e676` | Confirmation toasts & "Applied to Windows" badges |
| **Warning Amber** | `#ffb703` | Notice alerts & Help Select badges |
| **Danger Coral** | `#ff3838` | Unavailable / Revert warnings |
| **Text Primary** | `#f8f9fc` | High contrast headings and labels |
| **Text Muted** | `#8c94ab` | Subtitles, descriptions, and hotspot coordinates |

### Typography
- **Primary Font**: `Inter`, `Segoe UI Variable Display`, system sans-serif.
- **Monospace Font**: `JetBrains Mono`, `Consolas` (for Hex values, coordinates, and DPI metrics).

---

## 2. Layout & Information Architecture

The UI is divided into a **Dual Studio Layout**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  CURSOR CONCEPT  [v1.0]           [Active Scheme: Moga Purple]       [Profile: Custom ▾]   [_  □  ✕]   │
├────────────────────────────────┬────────────────────────────────────────────────────────────────────────┤
│  LEFT CONTROLS SIDEBAR (380px) │  MAIN STAGE (Flex Canvas)                                              │
│                                │                                                                        │
│  [MODE: Solid | Gradient | RGB]│  ┌──────────────────────────────────────────────────────────────────┐  │
│  • Fill Color Pickers          │  │  INTERACTIVE TEST SANDBOX                                        │  │
│  • Gradient Angle Dial (0° to 360°) │  [ Move mouse here to live test your cursor with physics & trail]│  │
│  • Outline: White / Black / Hex│  └──────────────────────────────────────────────────────────────────┘  │
│  • Loading Spinner Hue         │                                                                        │
│                                │  REAL ICON SHELVES (34 Transformations)                                │
│  CURATED PRESETS CAROUSEL      │  ┌──────────────────────────────────────────────────────────────────┐  │
│  [Moga] [Sakura] [Cyber]       │  │  1. Pointers & Selection (Normal, Link, Alt, Precision, Menu)    │  │
│  [Mint] [Sunset] [Onyx]        │  ├──────────────────────────────────────────────────────────────────┤  │
│                                │  │  2. Window Splitters & Resizers (Col/Row Capacitor, Horz, Vert)  │  │
│  EXPORT & BUILD OPTIONS        │  ├──────────────────────────────────────────────────────────────────┤  │
│  • Include HDPI (32,48,64,96px)│  │  3. Text Editing & Drawing (I-Beam, Vertical Text, Handwriting)   │  │
│  • Generate INFs               │  ├──────────────────────────────────────────────────────────────────┤  │
│                                │  │  4. Navigation & Drag (4 Way Move, Hand, Fist, Zoom, Copy, Alias) │  │
│  [APPLY TO WINDOWS DIRECTLY]   │  └──────────────────────────────────────────────────────────────────┘  │
│  [EXPORT PACK] [REVERT]        │                                                                        │
└────────────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```

### Component Details
1. **Left Controls Sidebar**:
   - **Fill Mode Switcher**: Three tabs:
     - **Solid**: Hex input with instant visual swatch and native eyedropper.
     - **Side / Linear Gradient**: Two color stops (Color A $\rightarrow$ Color B) + 360° spatial angle slider.
     - **Chroma RGB Continuous Wave**: Razer Chroma style rainbow wave with animation speed slider (0.5x to 3.0x).
   - **Outer Border Controller**: Toggle between White (`#ffffff`), Black (`#000000`), or Custom Hex, plus outline thickness slider.
   - **Loading Spinner Selector**: Theme matching, Classic Blue, Indigo, Rainbow, or Custom Accent.
   - **Curated Presets**: One click styling templates.

2. **Interactive Test Sandbox**:
   - A dedicated live testing card in the center. Moving the pointer over this area immediately changes the pointer into the generated cursor using high performance CSS `cursor: url(...)` injection.
   - Includes an optional "Cursor Trail" or "Click Particle" toggle to test responsiveness.
3. **Real Icon Shelves (34 Transformations)**:
   - Categorized trays displaying true pixel buffers (not AI approximations) at 2x zoom for clarity.
   - Displays real time hotspots $(x, y)$ and resolution tags (`HDPI: 32 to 96px`).


---

## 3. Backend Engine & System Integration

### Technical Stack
- **Desktop Host**: `pywebview` utilizing Microsoft Edge WebView2 (Chromium).
- **Core Engine**: Python 3.14 + `Pillow` + `NumPy`.
- **Packaging**: Single standalone binary `Cursor Concept.exe` compiled via PyInstaller.

### Bidirectional Python $\leftrightarrow$ JavaScript Bridge
The app uses an asynchronous JSON-RPC IPC bridge provided by `pywebview`:

```javascript
// Frontend calls Python backend directly:
await window.pywebview.api.apply_to_windows({
    mode: "gradient",
    colorA: "#a6a3ff",
    colorB: "#00f0ff",
    angle: 45,
    outline: "#ffffff",
    spinnerColor: "#a6a3ff",
    enableChroma: false
});
```

### Python Backend Subsystems
1. **Mathematical Spatial Shader (`engine/recolor.py`)**:
   - Computes linear gradients using 2D projection:
     $$p(x, y) = x \cos \theta + y \sin \theta$$
     $$t = \frac{p(x, y) - p_{\min}}{p_{\max} - p_{\min}}$$
     $$\text{Color}(x, y) = (1 - t) \cdot C_1 + t \cdot C_2$$
   - Interpolates antialiased transitions between the body fill and the outer border.
   - Retains authentic drop shadows with preserved alpha ramps.
2. **Multi Resolution HDPI Compiler (`engine/cur_builder.py`)**:
   - Packs every `.cur` file with 4 uncompressed 32-bit ARGB DIB layers:
     `[32x32, 48x48, 64x64, 96x96]`
   - Generates exact 1-bit AND transparency masks for 100% Windows legacy compatibility.
   - Compiles 32 frame `.ani` RIFF ACON animated containers for spinners and 36 frame `.ani` files for Chroma RGB wave pointers.
3. **Win32 System Live Apply Engine (`engine/win_cursor_api.py`)**:
   - **Registry Writer**: Registers the generated scheme into `HKCU\Control Panel\Cursors\Schemes` and activates it in `HKCU\Control Panel\Cursors`.
   - **Accessibility Auto Healer**: Automatically verifies and sets `HKCU\Software\Microsoft\Accessibility\CursorType` to `0`, preventing Windows 11 from overriding text selection or moving cursors with white defaults.
   - **Live System Broadcast**: Calls `ctypes.windll.user32.SystemParametersInfoW(0x0057, 0, None, 0)` (`SPI_SETCURSORS`), forcing the entire desktop and all running apps to adopt the new cursor immediately without requiring a restart or opening Mouse Properties!

---

## 4. The 34 Cursor Transformation Matrix

The application includes, previews, and exports all 34 cursor states:

| Index | Name | Role & Visual Identifier | OS & App Mapping |
| :---: | :--- | :--- | :--- |
| **01** | `Normal Select` | Primary navigation pointer arrow | `Arrow` |
| **02** | `Help Select` | Arrow with orange `?` question badge | `Help` |
| **03** | `Working in Background` | Arrow with rotating loading spinner | `AppStarting` |
| **04** | `Busy` | Standalone rotating loading spinner | `Wait` |
| **05** | `Precision Select` | Fine reticle / crosshair | `Crosshair` |
| **06** | `Text Select` | Vertical I-beam text insertion cursor | `IBeam` |
| **07** | `Handwriting` | Fine point angled pencil with eraser tip | `NWPen` |
| **08** | `Unavailable` | Arrow with red circle slash prohibited symbol | `No` |
| **09** | `Vertical Resize` | Vertical double headed arrow ($\updownarrow$) | `SizeNS` |
| **10** | `Horizontal Resize` | Horizontal double headed arrow ($\leftrightarrow$) | `SizeWE` |
| **11** | `Diagonal Resize 1` | Diagonal NW-SE double headed arrow ($\searrow\nwarrow$) | `SizeNWSE` |
| **12** | `Diagonal Resize 2` | Diagonal NE-SW double headed arrow ($\nearrow\swarrow$) | `SizeNESW` |
| **13** | `Move (4 Way)` | 4 directional arrow cross ($\large\bm{+}$) | `SizeAll` |
| **14** | `Alternate Select` | Upward / rightward pointing secondary arrow | `UpArrow` |
| **15** | `Link Select` | Pointing interactive hand | `Hand` |
| **16** | `Location Select` | Map marker location pin with inner dot | `Pin` |
| **17** | `Person Select` | Profile contact avatar silhouette | `Person` |
| **18** | **`Column Resize (Split H)`** | **Capacitor style double bar with outward arrows ($\| \leftrightarrow \|$)** | `col-resize` |
| **19** | **`Row Resize (Split V)`** | **Capacitor style double bar with up/down arrows** | `row-resize` |
| **20** | `Move (Open Hand)` | Open hand for document panning / grabbing | `grab` |
| **21** | `Move (Closed Fist)` | Closed fist while actively dragging | `grabbing` |
| **22** | `Zoom In` | Magnifying glass with centered `+` | `zoom-in` |
| **23** | `Zoom Out` | Magnifying glass with centered `-` | `zoom-out` |
| **24** | `Context Menu` | Pointer arrow with mini popup menu badge | `context-menu` |
| **25** | `Cell Select` | Thick cross for spreadsheet selection | `cell` |
| **26** | `Vertical Text` | Horizontal I-beam for vertical text blocks | `vertical-text` |
| **27** | `Drag Copy` | Pointer arrow with green `+` badge | `copy` |
| **28** | `Drag Alias` | Pointer arrow with curved shortcut arrow badge | `alias` |
| **29** | `Drag No Drop` | Pointer arrow with prohibited drop badge | `no-drop` |
| **30** | `North Resize` | Single arrow pointing North | `n-resize` |
| **31** | `South Resize` | Single arrow pointing South | `s-resize` |
| **32** | `East Resize` | Single arrow pointing East | `e-resize` |
| **33** | `West Resize` | Single arrow pointing West | `w-resize` |
| **34** | `Color Picker` | Eyedropper pipette sampling tool | `color-picker` |

---

## 5. Quality of Life (QoL) Features

1. **Zero Reboot Instant Activation**:
   - Single click "Apply to Windows" directly updates the OS. No opening `main.cpl`, no manual dropdown searching, and no Windows restart required.
2. **Continuous Chroma RGB Cycling Mode**:
   - Generates animated `.ani` pointers that cycle through the full color spectrum smoothly, turning your mouse into a gaming Chroma device.
3. **360° Visual Gradient Dial**:
   - Drag an intuitive rotary dial or enter an exact angle in degrees to align your side gradient or diagonal flow.
4. **Built in Eyedropper & Color Picker**:
   - Use the native screen eyedropper to sample any color directly from your desktop wallpaper, code editor, or browser.
5. **Live Mouse Sandbox Pad**:
   - Move your mouse over an in app testing canvas to try out your new cursor with realistic tracking before applying it to your system.

6. **1 Click Panic Revert**:
   - Dedicated "Restore Windows Default" button instantly restores original `Windows Aero` cursors and clears any overrides.
7. **Full Multi Resolution HDPI Exporter**:
   - Exports all 34 cursors with automatically formatted `Install.inf` and `Uninstall.inf` for easy backup and distribution.
8. **Display DPI Auto Calibration**:
   - Detects the monitor's active scale factor (e.g. your 125% scale, 120 DPI) and automatically tunes the HDPI mipmap priorities.
9. **Custom Profile Manager**:
   - Save your favorite color combinations and gradients as `.json` profiles and switch between them in seconds.

---

## 6. Attribution & Design Heritage

The core visual geometry, cursor silhouettes, and transformation metaphors are based upon the celebrated *Windows 11 Cursor Concept* created by **jepriCreations** ([jepricreations.com](https://jepricreations.com/) and [DeviantArt: jepriCreations](https://www.deviantart.com/jepricreations)). This application serves as a standalone software runtime and shader workbench built around that design aesthetic.
