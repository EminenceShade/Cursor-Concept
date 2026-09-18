import os
import io
import math
import base64
import colorsys
import struct
from PIL import Image
from typing import Dict, List, Tuple, Any

from .cur_builder import read_cur_data, pack_cur_entry, build_multires_cur, build_ani_file, parse_ani_frames
from .recolor import hex_to_rgb, rgb_to_hex, recolor_cursor_image
from .chroma import build_chroma_cursor_ani
from .cursor_data import CURSOR_CATALOG, get_base_cursor_image, DARK_DIR
from .win_api import apply_cursor_scheme, revert_to_windows_default, get_current_scheme_name

APP_DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "CursorConcept")
ACTIVE_THEME_DIR = os.path.join(APP_DATA_DIR, "active")

def get_multi_res_layers(base_32_img: Image.Image, base_hotspot: Tuple[int, int]) -> List[Tuple[Image.Image, Tuple[int, int]]]:
    """
    Generates multi-resolution layers: 32px, 48px, 64px, 96px.
    """
    layers = [(base_32_img, base_hotspot)]
    for target_sz, factor in [(48, 1.5), (64, 2.0), (96, 3.0)]:
        scaled = base_32_img.resize((target_sz, target_sz), Image.Resampling.LANCZOS)
        new_hot = (round(base_hotspot[0] * factor), round(base_hotspot[1] * factor))
        layers.append((scaled, new_hot))
    return layers

def recolor_ani_cursor(base_ani_path: str, fill_mode: str, color_a: Tuple[int, int, int], color_b: Tuple[int, int, int], angle: float, outline_color: Tuple[int, int, int], base_type: str = "dark", jif_rate: int = 2) -> bytes:
    """
    Recolors an animated cursor (Busy or Working In Background).
    """
    _, raw_cur_frames = parse_ani_frames(base_ani_path)
    
    if base_type == "black":
        base_type = "dark"

    # Calculate target hue from color_a for the spinner particles
    r_n, g_n, b_n = [c / 255.0 for c in color_a]
    target_hue, s_a, v_a = colorsys.rgb_to_hsv(r_n, g_n, b_n)
    if s_a < 0.1:
        r_o, g_o, b_o = [c / 255.0 for c in outline_color]
        h_o, s_o, v_o = colorsys.rgb_to_hsv(r_o, g_o, b_o)
        if s_o >= 0.1:
            target_hue = h_o
    
    recolored_frames = []
    for cur_bytes in raw_cur_frames:
        reserved, type_, count = struct.unpack("<HHH", cur_bytes[:6])
        w, h, colors, res, x_hot, y_hot, bytes_in_res, offset = struct.unpack("<BBBBHHII", cur_bytes[6:22])
        actual_w = 256 if w == 0 else w
        actual_h = 256 if h == 0 else h
        
        dib = cur_bytes[offset:]
        raw_pixels = dib[40:40 + actual_w * actual_h * 4]
        img = Image.frombytes("RGBA", (actual_w, actual_h), raw_pixels, "raw", "BGRA")
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        
        out = Image.new("RGBA", (actual_w, actual_h))
        w_img, h_img = img.size
        
        for y in range(h_img):
            for x in range(w_img):
                r, g, b, a = img.getpixel((x, y))
                if a == 0:
                    out.putpixel((x, y), (0, 0, 0, 0))
                    continue
                
                # Check for spinner particle (blue in original Moga)
                if (b > r + 25) and (b > g + 20) and b > 60:
                    h_val, s_val, v_val = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
                    nr, ng, nb = colorsys.hsv_to_rgb(target_hue, s_val, v_val)
                    out.putpixel((x, y), (round(nr*255), round(ng*255), round(nb*255), a))
                    continue
                    
                # Arrow / base body
                max_diff = max(abs(r - g), abs(g - b), abs(r - b))
                if max_diff <= 3:
                    if r < 18 and a < 160: # shadow
                        out.putpixel((x, y), (r, g, b, a))
                        continue
                    v = (r + g + b) / 3.0
                    if base_type == "dark":
                        if v <= 26.0:
                            out.putpixel((x, y), (color_a[0], color_a[1], color_a[2], a))
                        elif v >= 250.0:
                            out.putpixel((x, y), (outline_color[0], outline_color[1], outline_color[2], a))
                        else:
                            t = (v - 26.0) / (255.0 - 26.0)
                            t = max(0.0, min(1.0, t))
                            nr = round((1.0 - t) * color_a[0] + t * outline_color[0])
                            ng = round((1.0 - t) * color_a[1] + t * outline_color[1])
                            nb = round((1.0 - t) * color_a[2] + t * outline_color[2])
                            out.putpixel((x, y), (nr, ng, nb, a))
                    else: # white base
                        if v >= 245.0:
                            out.putpixel((x, y), (color_a[0], color_a[1], color_a[2], a))
                        elif v <= 30.0:
                            out.putpixel((x, y), (outline_color[0], outline_color[1], outline_color[2], a))
                        else:
                            t = v / 255.0
                            t = max(0.0, min(1.0, t))
                            nr = round(t * color_a[0] + (1.0 - t) * outline_color[0])
                            ng = round(t * color_a[1] + (1.0 - t) * outline_color[1])
                            nb = round(t * color_a[2] + (1.0 - t) * outline_color[2])
                            out.putpixel((x, y), (nr, ng, nb, a))
                else:
                    out.putpixel((x, y), (r, g, b, a))
                    
        frame_data, hot = pack_cur_entry(out, (x_hot, y_hot))
        w_byte = actual_w if actual_w < 256 else 0
        h_byte = actual_h if actual_h < 256 else 0
        hdr = struct.pack("<HHH", 0, 2, 1)
        ent = struct.pack("<BBBBHHII", w_byte, h_byte, 0, 0, hot[0], hot[1], len(frame_data), 22)
        recolored_frames.append(hdr + ent + frame_data)
        
    return build_ani_file(recolored_frames, jif_rate=jif_rate)

def build_inf_content(scheme_name: str, cursor_files: Dict[str, str], all_filenames: List[str] = None) -> str:
    """Generates standard Windows Setup Information (.inf) file."""
    lines = [
        "[Version]",
        'signature="$CHICAGO$" ',
        f'DisplayName="{scheme_name}"',
        "",
        "[DefaultInstall]",
        "CopyFiles = Scheme.Cur, Scheme.Txt",
        "AddReg    = Scheme.Reg",
        "",
        "[DestinationDirs]",
        "Scheme.Cur = 10,%CUR_DIR%",
        "Scheme.Txt = 10,%CUR_DIR%",
        "",
        "[Scheme.Reg]",
        f'HKCU,"Control Panel\\Cursors\\Schemes","{scheme_name}",,"%10%\\%CUR_DIR%\\%pointer%,%10%\\%CUR_DIR%\\%help%,%10%\\%CUR_DIR%\\%work%,%10%\\%CUR_DIR%\\%busy%,%10%\\%CUR_DIR%\\%cross%,%10%\\%CUR_DIR%\\%Text%,%10%\\%CUR_DIR%\\%Hand%,%10%\\%CUR_DIR%\\%unavailiable%,%10%\\%CUR_DIR%\\%Vert%,%10%\\%CUR_DIR%\\%Horz%,%10%\\%CUR_DIR%\\%Dgn1%,%10%\\%CUR_DIR%\\%Dgn2%,%10%\\%CUR_DIR%\\%move%,%10%\\%CUR_DIR%\\%alternate%,%10%\\%CUR_DIR%\\%link%,%10%\\%CUR_DIR%\\%pin%,%10%\\%CUR_DIR%\\%person%"',
        "",
        "[Scheme.Cur]",
    ]
    files_to_list = all_filenames if all_filenames else list(cursor_files.values())
    for fn in files_to_list:
        lines.append(f'"{fn}"')
        
    lines.extend([
        "",
        "[Strings]",
        f'CUR_DIR       = "Cursors\\{scheme_name}"',
        f'SCHEME_NAME   = "{scheme_name}"',
        f'pointer       = "{cursor_files.get("Arrow", "Normal Select.cur")}"',
        f'help          = "{cursor_files.get("Help", "Help Select.cur")}"',
        f'work          = "{cursor_files.get("AppStarting", "Working In Background.ani")}"',
        f'busy          = "{cursor_files.get("Wait", "Busy.ani")}"',
        f'cross         = "{cursor_files.get("Crosshair", "Precision Select.cur")}"',
        f'text          = "{cursor_files.get("IBeam", "Text Select.cur")}"',
        f'hand          = "{cursor_files.get("NWPen", "HandWriting.cur")}"',
        f'unavailiable  = "{cursor_files.get("No", "Unavailable.cur")}"',
        f'vert          = "{cursor_files.get("SizeNS", "Vertical Resize.cur")}"',
        f'horz          = "{cursor_files.get("SizeWE", "Horizontal Resize.cur")}"',
        f'dgn1          = "{cursor_files.get("SizeNWSE", "Diagonal Resize 1.cur")}"',
        f'dgn2          = "{cursor_files.get("SizeNESW", "Diagonal Resize 2.cur")}"',
        f'move          = "{cursor_files.get("SizeAll", "Move.cur")}"',
        f'alternate     = "{cursor_files.get("UpArrow", "Alternate Select.cur")}"',
        f'link          = "{cursor_files.get("Hand", "Link Select.cur")}"',
        f'pin           = "{cursor_files.get("Pin", "Location Select.cur")}"',
        f'person        = "{cursor_files.get("Person", "Person Select.cur")}"',
    ])
    return "\r\n".join(lines)

def build_uninstall_inf(scheme_name: str) -> str:
    """Generates standard Windows Uninstall Information (.inf) file."""
    return "\r\n".join([
        "[Version]",
        'signature="$CHICAGO$" ',
        "",
        "[DefaultInstall]",
        "DelReg = Scheme.DelReg",
        "",
        "[Scheme.DelReg]",
        f'HKCU,"Control Panel\\Cursors\\Schemes","{scheme_name}"',
        "",
        "[Strings]",
        f'SCHEME_NAME = "{scheme_name}"',
    ])

class ThemeEngine:
    def __init__(self):
        pass

    def generate_theme_files(self, config: Dict[str, Any], output_dir: str) -> Dict[str, str]:
        """
        Generates all cursor files (.cur/.ani) according to config into output_dir.
        Returns dict mapping OS key ("Arrow", "Help", etc.) to absolute file path.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        mode = config.get("mode", "solid") # solid, gradient, chroma
        color_a = hex_to_rgb(config.get("color_a", "#a6a3ff"))
        color_b = hex_to_rgb(config.get("color_b", "#00f0ff"))
        angle = float(config.get("angle", 45))
        outline_color = hex_to_rgb(config.get("outline_color", "#ffffff"))
        base_type = config.get("base_type", "dark")
        is_chroma = (mode == "chroma" or mode == "rgb")
        rgb_speed = int(config.get("rgb_speed", 2))
        rgb_direction = str(config.get("rgb_direction", "clockwise"))
        jif_rate_map = {1: 4, 2: 2, 3: 2, 4: 1}
        chroma_jif = jif_rate_map.get(rgb_speed, 2)
        chroma_frames = 24 if rgb_speed == 3 else 36
        
        os_key_map = {}
        filenames_map = {}
        all_filenames = []

        for item in CURSOR_CATALOG:
            cid = item["id"]
            filename = item["file"]
            all_filenames.append(filename)
            hotspot = item["hotspot"]
            os_key = item.get("os_key")
            is_anim = item.get("is_anim", False)
            out_path = os.path.join(output_dir, filename)

            if is_anim:
                # Busy or Working In Background
                base_ani_path = os.path.join(DARK_DIR, filename)
                if is_chroma:
                    # Chroma RGB wave for animated spinners
                    base_img, hot = get_base_cursor_image(cid)
                    ani_bytes = build_chroma_cursor_ani(
                        base_img=base_img,
                        hotspot=hot,
                        num_frames=chroma_frames,
                        jif_rate=chroma_jif,
                        outline_color=outline_color,
                        base_type=base_type,
                        direction=rgb_direction
                    )
                else:
                    ani_bytes = recolor_ani_cursor(
                        base_ani_path=base_ani_path,
                        fill_mode=mode,
                        color_a=color_a,
                        color_b=color_b,
                        angle=angle,
                        outline_color=outline_color,
                        base_type=base_type,
                        jif_rate=2 # 30 FPS
                    )
                with open(out_path, "wb") as f:
                    f.write(ani_bytes)
            else:
                # Static cursor or Chroma-animated cursor
                base_img, hot = get_base_cursor_image(cid)
                if is_chroma and cid in ["normal", "link", "move_4way", "col_resize", "row_resize"]:
                    # In Chroma mode, main interaction cursors become animated .ani files!
                    ani_filename = filename.replace(".cur", ".ani")
                    out_path = os.path.join(output_dir, ani_filename)
                    ani_bytes = build_chroma_cursor_ani(
                        base_img=base_img,
                        hotspot=hot,
                        num_frames=chroma_frames,
                        jif_rate=chroma_jif,
                        outline_color=outline_color,
                        base_type=base_type,
                        direction=rgb_direction
                    )
                    with open(out_path, "wb") as f:
                        f.write(ani_bytes)
                    filename = ani_filename
                else:
                    recolored = recolor_cursor_image(
                        base_img,
                        fill_mode=mode,
                        color_a=color_a,
                        color_b=color_b,
                        angle=angle,
                        outline_color=outline_color,
                        base_type=base_type,
                        cursor_id=cid
                    )
                    # Multi-resolution packaging for crisp HDPI scaling
                    layers = get_multi_res_layers(recolored, hot)
                    cur_bytes = build_multires_cur(layers)
                    with open(out_path, "wb") as f:
                        f.write(cur_bytes)

            if os_key:
                os_key_map[os_key] = out_path
                filenames_map[os_key] = filename

        # Generate INF files
        scheme_name = config.get("scheme_name", "Cursor Concept")
        inf_content = build_inf_content(scheme_name, filenames_map, all_filenames)
        with open(os.path.join(output_dir, "Install.inf"), "w", encoding="utf-8") as f:
            f.write(inf_content)

        uninst_content = build_uninstall_inf(scheme_name)
        with open(os.path.join(output_dir, "Uninstall.inf"), "w", encoding="utf-8") as f:
            f.write(uninst_content)

        return os_key_map

    def get_previews_data(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates fast base64 PNG previews for all 34 cursor items.
        """
        mode = config.get("mode", "solid")
        color_a = hex_to_rgb(config.get("color_a", "#a6a3ff"))
        color_b = hex_to_rgb(config.get("color_b", "#00f0ff"))
        angle = float(config.get("angle", 45))
        outline_color = hex_to_rgb(config.get("outline_color", "#ffffff"))
        base_type = config.get("base_type", "dark")
        is_chroma = (mode == "chroma")

        previews = []
        for item in CURSOR_CATALOG:
            cid = item["id"]
            base_img, hot = get_base_cursor_image(cid)
            
            if is_chroma:
                # Render preview at rainbow gradient for chroma preview
                preview_img = recolor_cursor_image(
                    base_img,
                    fill_mode="gradient",
                    color_a=(255, 60, 120),
                    color_b=(0, 220, 255),
                    angle=45,
                    outline_color=outline_color,
                    base_type=base_type,
                    cursor_id=cid
                )
            else:
                preview_img = recolor_cursor_image(
                    base_img,
                    fill_mode=mode,
                    color_a=color_a,
                    color_b=color_b,
                    angle=angle,
                    outline_color=outline_color,
                    base_type=base_type,
                    cursor_id=cid
                )

            # High-DPI upscale (2x: 64x64) for crisp display in modern retina/high-DPI webviews
            display_img = preview_img.resize((64, 64), Image.Resampling.NEAREST)
            buf = io.BytesIO()
            display_img.save(buf, format="PNG")
            b64_str = base64.b64encode(buf.getvalue()).decode("ascii")

            previews.append({
                "id": cid,
                "name": item["name"],
                "category": item["category"],
                "hotspot": hot,
                "file": item["file"],
                "css_name": item.get("css_name", ""),
                "os_key": item.get("os_key", ""),
                "is_anim": item.get("is_anim", False),
                "data_url": f"data:image/png;base64,{b64_str}"
            })
            
        return previews

    def apply_theme_to_windows(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Generates theme into %LOCALAPPDATA%\\CursorConcept\\active and live-activates it.
        """
        try:
            scheme_name = config.get("scheme_name", "Cursor Concept")
            os_key_map = self.generate_theme_files(config, ACTIVE_THEME_DIR)
            success = apply_cursor_scheme(scheme_name, os_key_map)
            if success:
                return True, f"Successfully activated scheme '{scheme_name}' on Windows!"
            else:
                return False, "Failed to apply cursor scheme to Windows registry."
        except Exception as e:
            return False, f"Exception applying theme: {str(e)}"

    def revert_windows_default(self) -> Tuple[bool, str]:
        """Reverts Windows pointers back to default."""
        try:
            success = revert_to_windows_default()
            if success:
                return True, "Reverted Windows pointers to default."
            else:
                return False, "Failed to revert to default."
        except Exception as e:
            return False, f"Exception reverting pointers: {str(e)}"
