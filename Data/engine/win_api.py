import os
import sys
import winreg
import ctypes
import subprocess
from typing import Dict, Optional

# SPI_SETCURSORS constant
SPI_SETCURSORS = 0x0057
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

CURSOR_ROLES_ORDER = [
    "Arrow",
    "Help",
    "AppStarting",
    "Wait",
    "Crosshair",
    "IBeam",
    "NWPen",
    "No",
    "SizeNS",
    "SizeWE",
    "SizeNWSE",
    "SizeNESW",
    "SizeAll",
    "UpArrow",
    "Hand",
    "Pin",
    "Person"
]

OCR_MAPPINGS = {
    "Arrow": 32512,       # OCR_NORMAL
    "IBeam": 32513,       # OCR_IBEAM
    "Wait": 32514,        # OCR_WAIT
    "Crosshair": 32515,   # OCR_CROSS
    "UpArrow": 32516,     # OCR_UP
    "SizeNWSE": 32642,    # OCR_SIZENWSE
    "SizeNESW": 32643,    # OCR_SIZENESW
    "SizeWE": 32644,      # OCR_SIZEWE
    "SizeNS": 32645,      # OCR_SIZENS
    "SizeAll": 32646,     # OCR_SIZEALL
    "No": 32648,          # OCR_NO
    "Hand": 32649,        # OCR_HAND
    "AppStarting": 32650  # OCR_APPSTARTING
}

def set_accessibility_override_disabled() -> bool:
    """
    Ensure HKCU\\Software\\Microsoft\\Accessibility\\CursorType is 0.
    Windows 10/11 accessibility cursor overlay forces text selection (IBeam)
    and movement to default white pointers if CursorType != 0.
    """
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Accessibility")
        winreg.SetValueEx(key, "CursorType", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[win_api] Warning setting CursorType: {e}")
        return False

def live_swap_cursors_in_memory(cursor_files: Dict[str, str]) -> int:
    """
    Directly swaps cursors in active memory via SetSystemCursor.
    Immediately updates the mouse cursor on screen without waiting for window focus.
    """
    swapped = 0
    for role, ocr_id in OCR_MAPPINGS.items():
        path = cursor_files.get(role)
        if path and os.path.exists(path):
            try:
                # LoadCursorFromFile creates a handle which SetSystemCursor consumes and destroys
                hcur = ctypes.windll.user32.LoadCursorFromFileW(path)
                if hcur:
                    res = ctypes.windll.user32.SetSystemCursor(hcur, ocr_id)
                    if res:
                        swapped += 1
            except Exception as e:
                print(f"[win_api] Warning swapping {role}: {e}")
    return swapped

def reload_system_cursors() -> bool:
    """
    Invokes SystemParametersInfoW with SPI_SETCURSORS to force Windows Desktop
    Window Manager (DWM) and user32 to reload all system pointers.
    """
    try:
        res = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETCURSORS,
            0,
            None,
            SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        )
        return bool(res)
    except Exception as e:
        print(f"[win_api] Error reloading system cursors: {e}")
        return False

def apply_cursor_scheme(scheme_name: str, cursor_files: Dict[str, str]) -> bool:
    """
    1. Updates HKCU\\Control Panel\\Cursors with Scheme Source = 1
    2. Updates HKCU\\Control Panel\\Cursors\\Schemes
    3. Disables Accessibility override
    4. Swaps running cursor in memory via SetSystemCursor
    5. Live-reloads via SPI_SETCURSORS
    6. Broadcasts via UpdatePerUserSystemParameters
    """
    try:
        # 1. Update HKCU\Control Panel\Cursors
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Cursors")
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, scheme_name)
        winreg.SetValueEx(key, "Scheme Source", 0, winreg.REG_DWORD, 1)
        
        ordered_paths = []
        for role in CURSOR_ROLES_ORDER:
            path = cursor_files.get(role, "")
            ordered_paths.append(path)
            if path and os.path.exists(path):
                winreg.SetValueEx(key, role, 0, winreg.REG_SZ, path)
            elif role in cursor_files:
                winreg.SetValueEx(key, role, 0, winreg.REG_SZ, path)
        winreg.CloseKey(key)

        # 2. Update HKCU\Control Panel\Cursors\Schemes
        schemes_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Cursors\Schemes")
        scheme_csv = ",".join(ordered_paths)
        winreg.SetValueEx(schemes_key, scheme_name, 0, winreg.REG_EXPAND_SZ, scheme_csv)
        winreg.CloseKey(schemes_key)

        # 3. Disable accessibility override
        set_accessibility_override_disabled()

        # 4. Live reload via SystemParametersInfoW
        reload_system_cursors()

        # 5. Non-blocking asynchronous swap and broadcast
        def _async_post_apply():
            try:
                live_swap_cursors_in_memory(cursor_files)
                subprocess.Popen(["rundll32.exe", "user32.dll,UpdatePerUserSystemParameters"])
            except Exception:
                pass

        import threading
        t = threading.Thread(target=_async_post_apply, daemon=True)
        t.start()

        return True
    except Exception as e:
        print(f"[win_api] Error applying cursor scheme: {e}")
        return False

def revert_to_windows_default() -> bool:
    """
    Restores the standard Windows default / Windows Aero cursor scheme.
    """
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Cursors")
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Windows Default")
        winreg.SetValueEx(key, "Scheme Source", 0, winreg.REG_DWORD, 0)
        for role in CURSOR_ROLES_ORDER:
            try:
                winreg.SetValueEx(key, role, 0, winreg.REG_SZ, "")
            except Exception:
                pass
        winreg.CloseKey(key)

        set_accessibility_override_disabled()
        reload_system_cursors()

        try:
            subprocess.run(["rundll32.exe", "user32.dll,UpdatePerUserSystemParameters"], timeout=2, capture_output=True)
        except Exception:
            pass

        return True
    except Exception as e:
        print(f"[win_api] Error reverting cursor scheme: {e}")
        return False

def get_current_scheme_name() -> str:
    """Returns the currently active cursor scheme name from HKCU."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Cursors")
        val, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        return val or "Windows Default"
    except Exception:
        return "Windows Default"

SPI_GETMOUSESPEED = 0x0070
SPI_SETMOUSESPEED = 0x0071
SPI_GETWHEELSCROLLLINES = 0x0068
SPI_SETWHEELSCROLLLINES = 0x0069

def get_mouse_pointer_settings() -> Dict[str, int]:
    """Retrieves current Windows pointer speed (1-20) and wheel scroll lines."""
    speed = ctypes.c_int(10)
    scroll_lines = ctypes.c_int(3)
    try:
        ctypes.windll.user32.SystemParametersInfoW(SPI_GETMOUSESPEED, 0, ctypes.byref(speed), 0)
    except Exception:
        pass
    try:
        ctypes.windll.user32.SystemParametersInfoW(SPI_GETWHEELSCROLLLINES, 0, ctypes.byref(scroll_lines), 0)
    except Exception:
        pass
    return {
        "speed": speed.value,
        "scroll_lines": scroll_lines.value
    }

def set_mouse_pointer_settings(speed: Optional[int] = None, scroll_lines: Optional[int] = None) -> bool:
    """Updates Windows pointer speed (1-20) and wheel scroll lines in user profile."""
    try:
        if speed is not None:
            clamped_speed = max(1, min(20, int(speed)))
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETMOUSESPEED, 0, ctypes.c_void_p(clamped_speed), SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )
        if scroll_lines is not None:
            clamped_lines = max(1, min(50, int(scroll_lines)))
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETWHEELSCROLLLINES, clamped_lines, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )
        return True
    except Exception as e:
        print(f"[win_api] Failed to set pointer settings: {e}")
        return False

def get_system_display_info() -> Dict[str, Any]:
    """Retrieves active primary display resolution, DPI scaling percentage, and refresh rate."""
    try:
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                user32.SetProcessDPIAware()
            except Exception:
                pass

        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        hdc = user32.GetDC(0)
        refresh_rate = gdi32.GetDeviceCaps(hdc, 116)
        log_pixels_x = gdi32.GetDeviceCaps(hdc, 88)
        user32.ReleaseDC(0, hdc)

        dpi_pct = round((log_pixels_x / 96.0) * 100) if log_pixels_x else 100
        if refresh_rate <= 1:
            refresh_rate = 60

        return {
            "width": width,
            "height": height,
            "dpi": dpi_pct,
            "refresh_rate": refresh_rate,
            "display_str": f"{width}×{height} @ {dpi_pct}% DPI",
            "hz_str": f"{refresh_rate}Hz Sync"
        }
    except Exception as e:
        print(f"[win_api] Failed to get display info: {e}")
        return {
            "width": 1920,
            "height": 1080,
            "dpi": 100,
            "refresh_rate": 60,
            "display_str": "1920×1080 @ 100% DPI",
            "hz_str": "60Hz Sync"
        }

