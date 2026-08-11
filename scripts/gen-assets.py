#!/usr/bin/env python3
"""Generate favicon.svg, favicon.png, and og-image.png for the portfolio site.

Pure stdlib (zlib/struct) — no PIL/ImageMagick required.
"""
import math
import struct
import zlib

# ---------------------------------------------------------------- PNG writer

def _chunk(typ, data):
    return (struct.pack('>I', len(data)) + typ + data
            + struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff))


def write_png(path, w, h, px):
    """px: list of rows, each a list of (r, g, b, a) tuples."""
    raw = b''.join(b'\x00' + b''.join(bytes(p) for p in row) for row in px)
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)  # 8-bit RGBA
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(_chunk(b'IHDR', ihdr))
        f.write(_chunk(b'IDAT', zlib.compress(raw, 9)))
        f.write(_chunk(b'IEND', b''))


# ---------------------------------------------------------------- raster ops

def fill_polys(px, loops, color):
    """Even-odd scanline fill across multiple polygon loops (holes via nesting)."""
    h, w = len(px), len(px[0])
    for y in range(h):
        xs = []
        for pts in loops:
            for i in range(len(pts)):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % len(pts)]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            xa, xb = int(math.ceil(xs[i])), int(math.floor(xs[i + 1]))
            for x in range(max(0, xa), min(w, xb + 1)):
                px[y][x] = color


def fill_rect(px, x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(len(px), y1)):
        for x in range(max(0, x0), min(len(px[0]), x1)):
            px[y][x] = color


def rounded_rect(px, x0, y0, x1, y1, r, color):
    """Fill a rounded rectangle using an SDF test."""
    hw, hh = (x1 - x0) / 2, (y1 - y0) / 2
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for y in range(max(0, y0), min(len(px), y1)):
        for x in range(max(0, x0), min(len(px[0]), x1)):
            dx = max(abs(x + 0.5 - cx) - (hw - r), 0)
            dy = max(abs(y + 0.5 - cy) - (hh - r), 0)
            if dx * dx + dy * dy <= r * r:
                px[y][x] = color


# ---------------------------------------------------------------- pixel font

# 5x7 bitmap font, uppercase + digits + a few symbols
FONT = {
    'A': [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    'B': ["XXXX.", "X...X", "X...X", "XXXX.", "X...X", "X...X", "XXXX."],
    'C': [".XXXX", "X....", "X....", "X....", "X....", "X....", ".XXXX"],
    'D': ["XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX."],
    'E': ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"],
    'F': ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "X...."],
    'G': [".XXXX", "X....", "X....", "X.XXX", "X...X", "X...X", ".XXXX"],
    'H': ["X...X", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    'I': ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "XXXXX"],
    'J': ["..XXX", "...X.", "...X.", "...X.", "...X.", "X..X.", ".XX.."],
    'K': ["X...X", "X..X.", "X.X..", "XX...", "X.X..", "X..X.", "X...X"],
    'L': ["X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    'M': ["X...X", "XX.XX", "X.X.X", "X.X.X", "X...X", "X...X", "X...X"],
    'N': ["X...X", "XX..X", "X.X.X", "X..XX", "X...X", "X...X", "X...X"],
    'O': [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    'P': ["XXXX.", "X...X", "X...X", "XXXX.", "X....", "X....", "X...."],
    'Q': [".XXX.", "X...X", "X...X", "X...X", "X.X.X", "X..X.", ".XX.X"],
    'R': ["XXXX.", "X...X", "X...X", "XXXX.", "X.X..", "X..X.", "X...X"],
    'S': [".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."],
    'T': ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    'U': ["X...X", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    'V': ["X...X", "X...X", "X...X", "X...X", "X...X", ".X.X.", "..X.."],
    'W': ["X...X", "X...X", "X...X", "X.X.X", "X.X.X", "XX.XX", "X...X"],
    'X': ["X...X", "X...X", ".X.X.", "..X..", ".X.X.", "X...X", "X...X"],
    'Y': ["X...X", "X...X", ".X.X.", "..X..", "..X..", "..X..", "..X.."],
    'Z': ["XXXXX", "....X", "...X.", "..X..", ".X...", "X....", "XXXXX"],
    '0': [".XXX.", "X...X", "X..XX", "X.X.X", "XX..X", "X...X", ".XXX."],
    '1': ["..X..", ".XX..", "..X..", "..X..", "..X..", "..X..", ".XXX."],
    '2': [".XXX.", "X...X", "....X", "...X.", "..X..", ".X...", "XXXXX"],
    '3': ["XXXXX", "...X.", "..X..", "...X.", "....X", "X...X", ".XXX."],
    '4': ["...X.", "..XX.", ".X.X.", "X..X.", "XXXXX", "...X.", "...X."],
    '5': ["XXXXX", "X....", "XXXX.", "....X", "....X", "X...X", ".XXX."],
    '6': [".XXX.", "X....", "X....", "XXXX.", "X...X", "X...X", ".XXX."],
    '7': ["XXXXX", "....X", "...X.", "..X..", ".X...", ".X...", ".X..."],
    '8': [".XXX.", "X...X", "X...X", ".XXX.", "X...X", "X...X", ".XXX."],
    '9': [".XXX.", "X...X", "X...X", ".XXXX", "....X", "....X", ".XXX."],
    ' ': [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    '.': [".....", ".....", ".....", ".....", ".....", "..X..", "....."],
    '·': [".....", ".....", "..X..", ".....", ".....", ".....", "....."],
    '-': [".....", ".....", ".....", "XXXXX", ".....", ".....", "....."],
    '/': [".....", "....X", "...X.", "..X..", ".X...", "X....", "....."],
}


def draw_text(px, x, y, text, scale, color):
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[' '])
        for gy, row in enumerate(glyph):
            for gx, c in enumerate(row):
                if c == 'X':
                    fill_rect(px, x + gx * scale, y + gy * scale,
                              x + (gx + 1) * scale, y + (gy + 1) * scale, color)
        x += 6 * scale  # 5 wide + 1 spacing


def draw_a_mark(px, cx, top, size, color):
    """The 'A' logo mark: outer triangle minus inner triangle, plus crossbar."""
    b = top + size
    outer = [(cx, top), (cx - size * 0.4, b), (cx + size * 0.4, b)]
    inner = [(cx, top + size * 0.2), (cx - size * 0.27, b - size * 0.1),
             (cx + size * 0.27, b - size * 0.1)]
    fill_polys(px, [outer, inner], color)
    fill_rect(px, int(cx - size * 0.27), int(top + size * 0.62),
              int(cx + size * 0.27), int(top + size * 0.72), color)


# ---------------------------------------------------------------- palette

BG = (10, 10, 10, 255)
SURFACE = (18, 18, 18, 255)
GRID = (15, 15, 15, 255)
BORDER = (34, 34, 34, 255)
ACCENT = (0, 255, 178, 255)
TEXT = (229, 229, 229, 255)
MUTED = (136, 136, 136, 255)

# ---------------------------------------------------------------- favicon.png

S = 64
px = [[BG for _ in range(S)] for _ in range(S)]
rounded_rect(px, 0, 0, S, S, 14, BG)
draw_a_mark(px, S / 2, 6, 52, ACCENT)
write_png('favicon.png', S, S, px)

# ---------------------------------------------------------------- favicon.svg

with open('favicon.svg', 'w') as f:
    f.write('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#0a0a0a"/>
  <path d="M32 6 L54 58 H44 L32 26 L20 58 H10 Z" fill="#00ffb2"/>
  <rect x="20" y="38" width="24" height="6" fill="#00ffb2"/>
</svg>
''')

# ---------------------------------------------------------------- og-image.png

W, H = 1200, 630
px = [[BG for _ in range(W)] for _ in range(H)]

# faint grid
for x in range(0, W, 60):
    fill_rect(px, x, 0, x + 1, H, GRID)
for y in range(0, H, 60):
    fill_rect(px, 0, y, W, y + 1, GRID)

# subtle frame
fill_rect(px, 24, 24, W - 24, 25, BORDER)
fill_rect(px, 24, H - 25, W - 24, H - 24, BORDER)
fill_rect(px, 24, 24, 25, H - 24, BORDER)
fill_rect(px, W - 25, 24, W - 24, H - 24, BORDER)

# logo mark
draw_a_mark(px, 135, 70, 110, ACCENT)

# name
draw_text(px, 80, 240, 'ALEC HUDSON', 8, TEXT)

# tagline
draw_text(px, 80, 340, 'MAKER · TINKERER · ALWAYS MID-PROJECT', 4, ACCENT)

# divider + accent segment
fill_rect(px, 80, 470, W - 80, 472, BORDER)
fill_rect(px, 80, 469, 200, 473, ACCENT)

# url
draw_text(px, 80, 500, 'ALECHUDSON.GITHUB.IO/PORTFOLIO-SITE', 3, MUTED)

write_png('og-image.png', W, H, px)
print('done: favicon.png, favicon.svg, og-image.png')
