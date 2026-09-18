import struct
import io
from PIL import Image

def read_cur_data(path_or_bytes):
    """
    Reads a .cur file or byte stream and returns the primary Image (RGBA) and hotspot.
    """
    if isinstance(path_or_bytes, (bytes, bytearray)):
        data = bytes(path_or_bytes)
    elif hasattr(path_or_bytes, "read"):
        data = path_or_bytes.read()
    else:
        with open(path_or_bytes, "rb") as f:
            data = f.read()
            
    reserved, type_, count = struct.unpack("<HHH", data[:6])
    assert type_ == 2, "Not a valid Windows cursor (.cur)"
    w, h, colors, res, x_hot, y_hot, bytes_in_res, offset = struct.unpack("<BBBBHHII", data[6:22])
    actual_w = 256 if w == 0 else w
    actual_h = 256 if h == 0 else h
    
    dib = data[offset:]
    biSize, biWidth, biHeight, biPlanes, biBitCount, biCompression, biSizeImage, biXPels, biYPels, biClrUsed, biClrImp = struct.unpack("<IIIHHIIIIII", dib[:40])
    raw_pixels = dib[40:40 + actual_w * actual_h * 4]
    img = Image.frombytes("RGBA", (actual_w, actual_h), raw_pixels, "raw", "BGRA")
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    return img, (x_hot, y_hot)

def pack_cur_entry(img, hotspot):
    """
    Converts a PIL RGBA Image and hotspot into an uncompressed 32-bit DIB entry with 1-bit AND mask.
    """
    actual_w, actual_h = img.size
    flipped = img.transpose(Image.FLIP_TOP_BOTTOM)
    bgra_pixels = flipped.tobytes("raw", "BGRA")
    
    # Standard 1-bit AND mask
    row_bytes = (actual_w + 31) // 32 * 4
    and_mask = bytearray(row_bytes * actual_h)
    for y in range(actual_h):
        for x in range(actual_w):
            r, g, b, a = flipped.getpixel((x, y))
            if a == 0:
                byte_idx = y * row_bytes + (x // 8)
                bit_idx = 7 - (x % 8)
                and_mask[byte_idx] |= (1 << bit_idx)
                
    dib_header = struct.pack(
        "<IIIHHIIIIII",
        40, actual_w, actual_h * 2, 1, 32, 0,
        len(bgra_pixels) + len(and_mask), 0, 0, 0, 0
    )
    image_data = dib_header + bgra_pixels + bytes(and_mask)
    return image_data, hotspot

def build_multires_cur(images_with_hotspots):
    """
    Takes a list of [(img, hotspot), ...] and serializes a multi-resolution Windows .cur file.
    Ordered from largest to smallest for optimal Windows HDPI shell resolution selection.
    """
    # Sort descending by resolution width
    sorted_layers = sorted(images_with_hotspots, key=lambda item: item[0].size[0], reverse=True)
    count = len(sorted_layers)
    header = struct.pack("<HHH", 0, 2, count)
    
    entries = []
    image_blocks = []
    current_offset = 6 + count * 16
    
    for img, hotspot in sorted_layers:
        data_block, hot = pack_cur_entry(img, hotspot)
        w, h = img.size
        w_byte = w if w < 256 else 0
        h_byte = h if h < 256 else 0
        entry = struct.pack("<BBBBHHII", w_byte, h_byte, 0, 0, hot[0], hot[1], len(data_block), current_offset)
        entries.append(entry)
        image_blocks.append(data_block)
        current_offset += len(data_block)
        
    return header + b"".join(entries) + b"".join(image_blocks)

def parse_ani_frames(path):
    """
    Reads a Windows .ani file and extracts header and raw icon frame bytes.
    """
    with open(path, "rb") as f:
        data = f.read()
    
    anih_idx = data.find(b"anih")
    anih_chunk = data[anih_idx+8:anih_idx+44]
    
    list_idx = data.find(b"LIST")
    assert list_idx != -1, "Not a valid RIFF ACON animated cursor"
    list_size = struct.unpack("<I", data[list_idx+4:list_idx+8])[0]
    pos = list_idx + 12
    end_pos = list_idx + 8 + list_size
    
    cur_frames = []
    while pos < end_pos:
        chunk_type = data[pos:pos+4]
        chunk_len = struct.unpack("<I", data[pos+4:pos+8])[0]
        pos += 8
        if chunk_type == b"icon":
            cur_data = data[pos:pos+chunk_len]
            cur_frames.append(cur_data)
        pos += chunk_len + (chunk_len % 2)
        
    return anih_chunk, cur_frames

def build_ani_file(cur_frames, jif_rate=2):
    """
    Builds a RIFF ACON animated cursor file.
    jif_rate: 1 = 60 FPS (16.6ms), 2 = 30 FPS (33.3ms).
    """
    num_frames = len(cur_frames)
    # anih structure: cbSize(4), nFrames(4), nSteps(4), cx(4), cy(4), bpc(4), nPlanes(4), jifRate(4), flags(4)
    # flags: 1 = icon format
    anih_chunk = struct.pack("<IIIIIIIII", 36, num_frames, num_frames, 0, 0, 0, 0, jif_rate, 1)
    
    fram_chunks = []
    for frame_cur_bytes in cur_frames:
        chunk = b"icon" + struct.pack("<I", len(frame_cur_bytes)) + frame_cur_bytes
        if len(frame_cur_bytes) % 2 != 0:
            chunk += b"\x00"
        fram_chunks.append(chunk)
        
    list_content = b"fram" + b"".join(fram_chunks)
    list_chunk = b"LIST" + struct.pack("<I", len(list_content)) + list_content
    anih_block = b"anih" + struct.pack("<I", len(anih_chunk)) + anih_chunk
    
    riff_content = b"ACON" + anih_block + list_chunk
    riff_file = b"RIFF" + struct.pack("<I", len(riff_content)) + riff_content
    return riff_file
