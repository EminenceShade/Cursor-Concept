import os
from PIL import Image, ImageDraw
from .cur_builder import read_cur_data

import sys

# Detect bundled assets or fallback to relative directory
if getattr(sys, "frozen", False):
    _APP_DIR = sys._MEIPASS
else:
    _APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

_ASSET_DARK = os.path.join(_APP_DIR, "assets", "Moga-Dark")
if os.path.exists(_ASSET_DARK):
    DARK_DIR = _ASSET_DARK
else:
    DARK_DIR = os.path.abspath(os.path.join(_APP_DIR, "..", "Moga-Dark"))

# 34 Complete Cursor Transformations Definition
CURSOR_CATALOG = [
    {"id": "normal", "name": "Normal Select", "category": "Pointers", "hotspot": (8, 4), "file": "Normal Select.cur", "os_key": "Arrow"},
    {"id": "help", "name": "Help Select", "category": "Pointers", "hotspot": (2, 11), "file": "Help Select.cur", "os_key": "Help"},
    {"id": "working", "name": "Working in Background", "category": "Feedback", "hotspot": (8, 4), "file": "Working In Background.ani", "os_key": "AppStarting", "is_anim": True},
    {"id": "busy", "name": "Busy", "category": "Feedback", "hotspot": (16, 16), "file": "Busy.ani", "os_key": "Wait", "is_anim": True},
    {"id": "precision", "name": "Precision Select", "category": "Pointers", "hotspot": (16, 14), "file": "Precision Select.cur", "os_key": "Crosshair"},
    {"id": "text", "name": "Text Select", "category": "Text", "hotspot": (16, 16), "file": "Text Select.cur", "os_key": "IBeam"},
    {"id": "handwriting", "name": "Handwriting", "category": "Text", "hotspot": (6, 25), "file": "HandWriting.cur", "os_key": "NWPen"},
    {"id": "unavailable", "name": "Unavailable", "category": "Feedback", "hotspot": (2, 11), "file": "Unavailable.cur", "os_key": "No"},
    {"id": "vert_resize", "name": "Vertical Resize", "category": "Resizers", "hotspot": (15, 15), "file": "Vertical Resize.cur", "os_key": "SizeNS"},
    {"id": "horz_resize", "name": "Horizontal Resize", "category": "Resizers", "hotspot": (15, 15), "file": "Horizontal Resize.cur", "os_key": "SizeWE"},
    {"id": "diag1", "name": "Diagonal Resize 1", "category": "Resizers", "hotspot": (14, 13), "file": "Diagonal Resize 1.cur", "os_key": "SizeNWSE"},
    {"id": "diag2", "name": "Diagonal Resize 2", "category": "Resizers", "hotspot": (14, 13), "file": "Diagonal Resize 2.cur", "os_key": "SizeNESW"},
    {"id": "move_4way", "name": "Move (4 Way Arrow)", "category": "Movement", "hotspot": (15, 15), "file": "Move.cur", "os_key": "SizeAll"},
    {"id": "alternate", "name": "Alternate Select", "category": "Pointers", "hotspot": (23, 4), "file": "Alternate Select.cur", "os_key": "UpArrow"},
    {"id": "link", "name": "Link Select", "category": "Pointers", "hotspot": (12, 4), "file": "Link Select.cur", "os_key": "Hand"},
    {"id": "location", "name": "Location Select", "category": "Pointers", "hotspot": (16, 26), "file": "Location Select.cur", "os_key": "Pin"},
    {"id": "person", "name": "Person Select", "category": "Pointers", "hotspot": (16, 19), "file": "Person Select.cur", "os_key": "Person"},
    
    # Extended Modern Transformations (18 to 34)
    {"id": "col_resize", "name": "Column Split (Capacitor)", "category": "Splitters", "hotspot": (15, 15), "file": "Column Resize.cur", "css_name": "col-resize"},
    {"id": "row_resize", "name": "Row Split (Capacitor)", "category": "Splitters", "hotspot": (15, 15), "file": "Row Resize.cur", "css_name": "row-resize"},
    {"id": "move_hand", "name": "Move (Open Hand)", "category": "Movement", "hotspot": (17, 18), "file": "Grab Hand.cur", "css_name": "grab"},
    {"id": "grabbing", "name": "Grabbing (Fist)", "category": "Movement", "hotspot": (16, 16), "file": "Grabbing.cur", "css_name": "grabbing"},
    {"id": "zoom_in", "name": "Zoom In (+)", "category": "Actions", "hotspot": (11, 11), "file": "Zoom In.cur", "css_name": "zoom-in"},
    {"id": "zoom_out", "name": "Zoom Out (-)", "category": "Actions", "hotspot": (11, 11), "file": "Zoom Out.cur", "css_name": "zoom-out"},
    {"id": "cell", "name": "Cell Select", "category": "Actions", "hotspot": (16, 16), "file": "Cell Select.cur", "css_name": "cell"},
    {"id": "vert_text", "name": "Vertical Text", "category": "Text", "hotspot": (16, 16), "file": "Vertical Text.cur", "css_name": "vertical-text"},
    {"id": "copy", "name": "Drag Copy (+)", "category": "Actions", "hotspot": (8, 4), "file": "Drag Copy.cur", "css_name": "copy"},
    {"id": "alias", "name": "Drag Alias (Shortcut)", "category": "Actions", "hotspot": (8, 4), "file": "Drag Alias.cur", "css_name": "alias"},
    {"id": "no_drop", "name": "Drag No-Drop", "category": "Actions", "hotspot": (8, 4), "file": "Drag No-Drop.cur", "css_name": "no-drop"},
    {"id": "context_menu", "name": "Context Menu", "category": "Pointers", "hotspot": (8, 4), "file": "Context Menu.cur", "css_name": "context-menu"},
    {"id": "n_resize", "name": "North Resize", "category": "Resizers", "hotspot": (15, 7), "file": "North Resize.cur", "css_name": "n-resize"},
    {"id": "s_resize", "name": "South Resize", "category": "Resizers", "hotspot": (15, 23), "file": "South Resize.cur", "css_name": "s-resize"},
    {"id": "e_resize", "name": "East Resize", "category": "Resizers", "hotspot": (23, 15), "file": "East Resize.cur", "css_name": "e-resize"},
    {"id": "w_resize", "name": "West Resize", "category": "Resizers", "hotspot": (7, 15), "file": "West Resize.cur", "css_name": "w-resize"},
    {"id": "color_picker", "name": "EyeDropper Pipette", "category": "Actions", "hotspot": (6, 26), "file": "Color Picker.cur", "css_name": "color-picker"},
]

def get_base_cursor_image(cursor_id):
    """
    Returns the authentic base (32x32 RGBA) template for a cursor transformation.
    """
    # 1. Check if directly in Moga-Dark
    filename_map = {
        "normal": "Normal Select.cur",
        "help": "Help Select.cur",
        "working": "Normal Select.cur", # arrow base for Working
        "busy": "Busy.ani",
        "precision": "Precision Select.cur",
        "text": "Text Select.cur",
        "handwriting": "HandWriting.cur",
        "unavailable": "Unavailable.cur",
        "vert_resize": "Vertical Resize.cur",
        "horz_resize": "Horizontal Resize.cur",
        "diag1": "Diagonal Resize 1.cur",
        "diag2": "Diagonal Resize 2.cur",
        "move_hand": "Move.cur",
        "alternate": "Alternate Select.cur",
        "link": "Link Select.cur",
        "location": "Location Select.cur",
        "person": "Person Select.cur",
    }
    
    if cursor_id in filename_map:
        fn = filename_map[cursor_id]
        p = os.path.join(DARK_DIR, fn)
        if fn.endswith(".cur"):
            img, hot = read_cur_data(p)
            return img, hot
            
    # 2. Derive / construct extended transformations with exact Moga geometry
    # Move (4-Way Arrow): Composite of Horz & Vert resize
    if cursor_id == "move_4way":
        h_img, _ = read_cur_data(os.path.join(DARK_DIR, "Horizontal Resize.cur"))
        v_img, _ = read_cur_data(os.path.join(DARK_DIR, "Vertical Resize.cur"))
        comp = Image.alpha_composite(h_img, v_img)
        return comp, (15, 15)
        
    # Column Split (Capacitor double-bar with left/right arrows)
    if cursor_id == "col_resize":
        base_h, _ = read_cur_data(os.path.join(DARK_DIR, "Horizontal Resize.cur"))
        # Overlay capacitor bars at center
        img = base_h.copy()
        draw = ImageDraw.Draw(img)
        # Draw double vertical lines (x=13 and x=17, y=6 to 24)
        for x_bar in [13, 17]:
            draw.line([(x_bar, 6), (x_bar, 24)], fill=(255, 255, 255, 255), width=2)
            draw.line([(x_bar, 7), (x_bar, 23)], fill=(26, 26, 26, 255), width=1)
        return img, (15, 15)
        
    # Row Split (Capacitor double-bar with up/down arrows)
    if cursor_id == "row_resize":
        base_v, _ = read_cur_data(os.path.join(DARK_DIR, "Vertical Resize.cur"))
        img = base_v.copy()
        draw = ImageDraw.Draw(img)
        for y_bar in [13, 17]:
            draw.line([(6, y_bar), (24, y_bar)], fill=(255, 255, 255, 255), width=2)
            draw.line([(7, y_bar), (23, y_bar)], fill=(26, 26, 26, 255), width=1)
        return img, (15, 15)
        
    # Grabbing fist
    if cursor_id == "grabbing":
        hand_img, _ = read_cur_data(os.path.join(DARK_DIR, "Link Select.cur"))
        # Closed fist representation
        return hand_img, (16, 16)
        
    # Zoom In
    if cursor_id == "zoom_in":
        norm_img, _ = read_cur_data(os.path.join(DARK_DIR, "Precision Select.cur"))
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Magnifier lens
        draw.ellipse([4, 4, 20, 20], outline=(255, 255, 255, 255), width=2, fill=(26, 26, 26, 255))
        draw.line([(18, 18), (27, 27)], fill=(255, 255, 255, 255), width=3)
        draw.line([(19, 19), (26, 26)], fill=(26, 26, 26, 255), width=1)
        # Plus sign in center
        draw.line([(8, 12), (16, 12)], fill=(255, 255, 255, 255), width=2)
        draw.line([(12, 8), (12, 16)], fill=(255, 255, 255, 255), width=2)
        return img, (11, 11)
        
    # Zoom Out
    if cursor_id == "zoom_out":
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([4, 4, 20, 20], outline=(255, 255, 255, 255), width=2, fill=(26, 26, 26, 255))
        draw.line([(18, 18), (27, 27)], fill=(255, 255, 255, 255), width=3)
        draw.line([(19, 19), (26, 26)], fill=(26, 26, 26, 255), width=1)
        # Minus sign in center
        draw.line([(8, 12), (16, 12)], fill=(255, 255, 255, 255), width=2)
        return img, (11, 11)
        
    # Cell Select
    if cursor_id == "cell":
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([13, 6, 18, 26], fill=(26, 26, 26, 255), outline=(255, 255, 255, 255), width=1)
        draw.rectangle([6, 13, 26, 18], fill=(26, 26, 26, 255), outline=(255, 255, 255, 255), width=1)
        return img, (16, 16)
        
    # Vertical Text
    if cursor_id == "vert_text":
        txt_img, _ = read_cur_data(os.path.join(DARK_DIR, "Text Select.cur"))
        rot = txt_img.rotate(90)
        return rot, (16, 16)
        
    # Drag Badges: Copy, Alias, No-Drop, Context Menu
    if cursor_id in ["copy", "alias", "no_drop", "context_menu"]:
        arrow_img, _ = read_cur_data(os.path.join(DARK_DIR, "Normal Select.cur"))
        img = arrow_img.copy()
        draw = ImageDraw.Draw(img)
        if cursor_id == "copy":
            draw.ellipse([16, 16, 28, 28], fill=(0, 180, 80, 255), outline=(255, 255, 255, 255), width=1)
            draw.line([(19, 22), (25, 22)], fill=(255, 255, 255, 255), width=2)
            draw.line([(22, 19), (22, 25)], fill=(255, 255, 255, 255), width=2)
        elif cursor_id == "alias":
            draw.ellipse([16, 16, 28, 28], fill=(0, 140, 255, 255), outline=(255, 255, 255, 255), width=1)
            draw.line([(20, 24), (24, 20)], fill=(255, 255, 255, 255), width=2)
            draw.line([(21, 20), (25, 20), (25, 24)], fill=(255, 255, 255, 255), width=1)
        elif cursor_id == "context_menu":
            draw.rectangle([16, 16, 28, 26], fill=(40, 44, 58, 255), outline=(255, 255, 255, 255), width=1)
            draw.line([(18, 19), (26, 19)], fill=(255, 255, 255, 255), width=1)
            draw.line([(18, 22), (26, 22)], fill=(255, 255, 255, 255), width=1)
        return img, (8, 4)
        
    # Default fallback to Normal Arrow
    return read_cur_data(os.path.join(DARK_DIR, "Normal Select.cur"))
