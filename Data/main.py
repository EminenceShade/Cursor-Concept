import os
import sys
import subprocess
import webview
from typing import Dict, Any

# Adjust paths when packaged with PyInstaller
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

from engine.theme_generator import ThemeEngine
from engine.win_api import get_mouse_pointer_settings, set_mouse_pointer_settings, get_system_display_info

_ACTIVE_WINDOW = None

class BridgeAPI:
    def __init__(self):
        self.engine = ThemeEngine()

    def get_display_info(self):
        """Returns current hardware display resolution, DPI scale, and refresh rate."""
        return get_system_display_info()

    def get_pointer_settings(self):
        """Returns current Windows mouse sensitivity and scroll lines."""
        return get_mouse_pointer_settings()

    def set_pointer_settings(self, data: Dict[str, Any]):
        """Sets Windows mouse sensitivity and/or scroll lines."""
        speed = data.get("speed")
        scroll_lines = data.get("scroll_lines")
        success = set_mouse_pointer_settings(speed=speed, scroll_lines=scroll_lines)
        return {"success": success}

    def get_previews(self, config: Dict[str, Any]):
        """Returns base64 previews of all 34 cursor transformations."""
        try:
            return self.engine.get_previews_data(config)
        except Exception as e:
            print(f"[BridgeAPI] Error generating previews: {e}")
            return []

    def apply_theme(self, config: Dict[str, Any]):
        """Generates and live-applies theme on Windows."""
        success, message = self.engine.apply_theme_to_windows(config)
        return {"success": success, "message": message}

    def revert_default(self):
        """Restores default Windows cursors."""
        success, message = self.engine.revert_windows_default()
        return {"success": success, "message": message}

    def export_theme(self, config: Dict[str, Any]):
        """Exports the full 34-cursor suite with INF files."""
        try:
            scheme_name = config.get("scheme_name", "Cursor Concept").replace("/", "-").replace("\\", "-")
            export_dir = None
            
            # Try folder picker dialog if window is active
            global _ACTIVE_WINDOW
            win = _ACTIVE_WINDOW or (webview.windows[0] if webview.windows else None)
            if win:
                res = win.create_file_dialog(webview.FOLDER_DIALOG)
                if res and len(res) > 0:
                    export_dir = os.path.join(res[0], scheme_name)
                    
            if not export_dir:
                export_dir = os.path.join(PROJECT_ROOT, "Exported Themes", scheme_name)

            os.makedirs(export_dir, exist_ok=True)
            self.engine.generate_theme_files(config, export_dir)

            # Open folder in Explorer
            subprocess.Popen(f'explorer "{export_dir}"')

            return {
                "success": True,
                "message": f"Exported theme to: {export_dir}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Export failed: {str(e)}"
            }

def main():
    global _ACTIVE_WINDOW
    api = BridgeAPI()
    html_path = os.path.join(BASE_DIR, "ui", "index.html")

    window = webview.create_window(
        title="Cursor Concept",
        url=html_path,
        js_api=api,
        width=1260,
        height=840,
        min_size=(1020, 700),
        background_color="#080a0f",
        text_select=False
    )
    _ACTIVE_WINDOW = window
    webview.start(debug=False)

if __name__ == "__main__":
    main()
