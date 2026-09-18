import colorsys
from PIL import Image
from .cur_builder import pack_cur_entry, build_ani_file
from .recolor import recolor_cursor_image

def generate_chroma_ani_frames(base_img, hotspot, num_frames=36, outline_color=(255, 255, 255), base_type="dark", direction="clockwise"):
    """
    Generates a list of .cur binary frames cycling through the full RGB color spectrum (0° -> 360° Hue).
    Supports 'clockwise' and 'counter_clockwise' spectral flow.
    """
    cur_frames = []
    w, h = base_img.size
    
    for i in range(num_frames):
        if direction == "counter_clockwise":
            hue = (num_frames - 1 - i) / float(num_frames)
        else:
            hue = i / float(num_frames)
            
        # Full vibrant saturation and value
        r, g, b = colorsys.hsv_to_rgb(hue, 0.75, 1.0)
        chroma_color = (round(r * 255), round(g * 255), round(b * 255))
        
        frame_img = recolor_cursor_image(
            base_img,
            fill_mode="solid",
            color_a=chroma_color,
            outline_color=outline_color,
            base_type=base_type
        )
        
        frame_data, hot = pack_cur_entry(frame_img, hotspot)
        w_byte = w if w < 256 else 0
        h_byte = h if h < 256 else 0
        
        import struct
        hdr = struct.pack("<HHH", 0, 2, 1)
        ent = struct.pack("<BBBBHHII", w_byte, h_byte, 0, 0, hot[0], hot[1], len(frame_data), 22)
        cur_frames.append(hdr + ent + frame_data)
        
    return cur_frames

def build_chroma_cursor_ani(base_img, hotspot, num_frames=36, jif_rate=1, outline_color=(255, 255, 255), base_type="dark", direction="clockwise"):
    """
    Builds a complete, ready-to-use Chroma RGB animated cursor (.ani) cycling at the specified jif_rate and direction.
    jif_rate: 1 = 60 FPS, 2 = 30 FPS, 3 = 20 FPS, 4 = 15 FPS.
    """
    frames = generate_chroma_ani_frames(
        base_img=base_img,
        hotspot=hotspot,
        num_frames=num_frames,
        outline_color=outline_color,
        base_type=base_type,
        direction=direction
    )
    return build_ani_file(frames, jif_rate=jif_rate)

