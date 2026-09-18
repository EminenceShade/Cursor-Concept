import math
from PIL import Image

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join([c*2 for c in hex_str])
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def compute_gradient_color(x, y, width, height, color_a, color_b, angle_deg):
    """
    Computes linear gradient color at coordinate (x, y) given angle in degrees.
    0 deg: Left -> Right (side gradient)
    90 deg: Top -> Bottom
    45 deg: Diagonal
    """
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    
    cx = width / 2.0
    cy = height / 2.0
    dx = x - cx
    dy = y - cy
    
    proj = dx * cos_a + dy * sin_a
    max_dist = abs(cx * cos_a) + abs(cy * sin_a)
    if max_dist < 1e-4:
        t = 0.5
    else:
        t = (proj + max_dist) / (2.0 * max_dist)
        
    t = max(0.0, min(1.0, t))
    r = round((1.0 - t) * color_a[0] + t * color_b[0])
    g = round((1.0 - t) * color_a[1] + t * color_b[1])
    b = round((1.0 - t) * color_a[2] + t * color_b[2])
    return (r, g, b)

def recolor_cursor_image(img, fill_mode="solid", color_a=(166, 163, 255), color_b=(0, 240, 255), angle=0, outline_color=(255, 255, 255), base_type="dark", cursor_id=""):
    """
    Precision shader that recolors a cursor image:
    - Supports solid color or 2D linear gradient fill at any angle
    - Custom outline color (White, Black, or arbitrary Hex)
    - Retains smooth anti-aliased edge blends
    - Retains authentic drop shadows
    - Unifies Location (pin) and Person (contact) into theme fill while preserving badges for Help (?) and Unavailable (no-entry)
    """
    out = Image.new("RGBA", img.size)
    w, h = img.size
    
    # Normalize base type
    if base_type == "black":
        base_type = "dark"
        
    for y in range(h):
        for x in range(w):
            r, g, b, a = img.getpixel((x, y))
            if a == 0:
                out.putpixel((x, y), (0, 0, 0, 0))
                continue
                
            # Check for drop shadow
            if base_type == "dark":
                if r < 20 and g < 20 and b < 20 and a < 160:
                    out.putpixel((x, y), (r, g, b, a))
                    continue
            else: # white base
                if r < 60 and g < 60 and b < 60 and a < 160:
                    out.putpixel((x, y), (r, g, b, a))
                    continue
                    
            # Compute fill color for this pixel (either solid or gradient)
            if fill_mode == "gradient":
                pixel_fill = compute_gradient_color(x, y, w, h, color_a, color_b, angle)
            else:
                pixel_fill = color_a

            # Special handling for Location Select & Person Select:
            # Re-color the pin and person body to match the theme!
            if cursor_id in ["location", "person"]:
                # White outline and inner highlight
                if r > 235 and g > 235 and b > 235:
                    out.putpixel((x, y), (outline_color[0], outline_color[1], outline_color[2], a))
                    continue
                v = (r + g + b) / 3.0
                if v > 200:
                    t = (v - 200.0) / 55.0
                    t = max(0.0, min(1.0, t))
                    nr = round((1.0 - t) * pixel_fill[0] + t * outline_color[0])
                    ng = round((1.0 - t) * pixel_fill[1] + t * outline_color[1])
                    nb = round((1.0 - t) * pixel_fill[2] + t * outline_color[2])
                    out.putpixel((x, y), (nr, ng, nb, a))
                else:
                    out.putpixel((x, y), (pixel_fill[0], pixel_fill[1], pixel_fill[2], a))
                continue

            # For other cursors, preserve accent badges (Help orange ?, Unavailable red stop circle, etc.)
            max_diff = max(abs(r - g), abs(g - b), abs(r - b))
            if max_diff > 4:
                out.putpixel((x, y), (r, g, b, a))
                continue

            # Process body, outline, and anti-aliasing based on base template
            v = (r + g + b) / 3.0
            
            if base_type == "dark":
                # Dark base: Body is ~26, Outline is 255
                if v <= 26.0:
                    out.putpixel((x, y), (pixel_fill[0], pixel_fill[1], pixel_fill[2], a))
                elif v >= 250.0:
                    out.putpixel((x, y), (outline_color[0], outline_color[1], outline_color[2], a))
                else:
                    t = (v - 26.0) / (255.0 - 26.0)
                    t = max(0.0, min(1.0, t))
                    nr = round((1.0 - t) * pixel_fill[0] + t * outline_color[0])
                    ng = round((1.0 - t) * pixel_fill[1] + t * outline_color[1])
                    nb = round((1.0 - t) * pixel_fill[2] + t * outline_color[2])
                    out.putpixel((x, y), (nr, ng, nb, a))
                    
            else: # white base
                # White base: Body is ~255, Outline is 0
                if v >= 245.0:
                    out.putpixel((x, y), (pixel_fill[0], pixel_fill[1], pixel_fill[2], a))
                elif v <= 30.0:
                    out.putpixel((x, y), (outline_color[0], outline_color[1], outline_color[2], a))
                else:
                    t = v / 255.0
                    t = max(0.0, min(1.0, t))
                    nr = round(t * pixel_fill[0] + (1.0 - t) * outline_color[0])
                    ng = round(t * pixel_fill[1] + (1.0 - t) * outline_color[1])
                    nb = round(t * pixel_fill[2] + (1.0 - t) * outline_color[2])
                    out.putpixel((x, y), (nr, ng, nb, a))
                    
    return out
