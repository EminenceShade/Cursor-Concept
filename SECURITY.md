# Security & System Safety Policy

## Architectural Safety Philosophy

Mouse cursors are fundamental to desktop operating system security. Flawed cursor software can introduce input lag, trigger anti cheat software, or even cause system instability. **Cursor Concept** is built upon strict safety principles:

### 1. Zero Hook Architecture
- **No Low Level Mouse Hooks (`WH_MOUSE_LL`)**: Low level mouse hooks intercept every subpixel mouse movement, which can introduce perceptible input latency on high refresh displays (144Hz to 360Hz).
- **No DLL Injection or API Hooking**: We never inject DLLs into third party processes or patch `user32.dll!SetCursor`. Such practices are commonly flagged by anti cheat systems (Riot Vanguard, Easy Anti-Cheat, BattlEye) and antivirus programs.
- **Pure Win32 Registry & Notification**: Cursor Concept interacts exclusively with standard Windows user settings (`HKCU\Control Panel\Cursors`) and broadcasts theme changes via the documented `SystemParametersInfoW(SPI_SETCURSORS)` Win32 API.


### 2. Non Elevated Standard User Execution
- `Cursor Concept.exe` executes completely within standard user permissions (`UAC: asInvoker`).
- It does **NOT** require Administrator privileges for daily theme application, color shading, or pack exporting.
- Only the standalone maintenance utility (`Tools/Reset.cmd`) requests elevation, and solely for cleaning legacy files inside `C:\Windows\Cursors\`.

### 3. Asynchronous Daemon Live Reload
- Win32 parameter updates are decoupled into an asynchronous daemon thread, ensuring the application UI thread never locks or freezes during system broadcasts.

---

## Reporting a Vulnerability

If you discover a security issue or unexpected system behavior, please report it responsibly:
- Email the maintainers directly or open a confidential security advisory on GitHub.
- Please provide your Windows version, display scaling percentage (DPI), and monitor refresh rate.
- We aim to respond within 48 hours to all security related reports.
