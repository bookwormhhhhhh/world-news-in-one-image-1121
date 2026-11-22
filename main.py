#!/usr/bin/env python3
"""WORLD NEWS - a one-page newspaper front page for 21 November 2026.

Draws a 1024x1024 PNG with nothing but the Python standard library:
a hand-made 5x7 bitmap font, simple drawing primitives and a small
PNG encoder built on zlib + struct.  Fully deterministic.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (243, 238, 226)
INK = (26, 26, 30)
NAVY = (17, 33, 63)
WHITE = (250, 248, 240)
ACCENT = (163, 36, 28)
GOLD = (206, 152, 30)
BLUE = (35, 63, 140)
GRAY = (96, 96, 100)
LIGHT = (214, 207, 190)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, seven rows of five pixels each.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#.##."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
}

img = bytearray(bytes(PAPER) * (W * H))


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        img[i] = color[0]
        img[i + 1] = color[1]
        img[i + 2] = color[2]


def rect_fill(x, y, w, h, color):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, color)


def rect_outline(x, y, w, h, color, t=1):
    rect_fill(x, y, w, t, color)
    rect_fill(x, y + h - t, w, t, color)
    rect_fill(x, y, t, h, color)
    rect_fill(x + w - t, y, t, h, color)


def line(x0, y0, x1, y1, color, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    off = t // 2
    while True:
        rect_fill(x0 - off, y0 - off, t, t, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle_fill(cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, color)


def polygon_fill(points, color):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    n = len(points)
    for yy in range(min(ys), max(ys) + 1):
        for xx in range(min(xs), max(xs) + 1):
            inside = False
            j = n - 1
            for i in range(n):
                xi, yi = points[i]
                xj, yj = points[j]
                if (yi > yy) != (yj > yy):
                    xint = (xj - xi) * (yy - yi) / (yj - yi) + xi
                    if xx < xint:
                        inside = not inside
                j = i
            if inside:
                px(xx, yy, color)


def clean(text):
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    return text.upper()


def text_width(text, scale, tracking=0):
    text = clean(text)
    if not text:
        return 0
    return len(text) * (6 * scale + tracking) - scale - tracking


def draw_text(x, y, text, scale, color, bold=False, tracking=0):
    text = clean(text)
    off = max(1, scale // 3) if bold else 0
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "#":
                    rect_fill(cx + col * scale, y + row * scale,
                              scale, scale, color)
                    if bold:
                        rect_fill(cx + col * scale + off, y + row * scale,
                                  scale, scale, color)
        cx += 6 * scale + tracking
    return cx - x


def draw_text_centered(cx, y, text, scale, color, bold=False, tracking=0):
    w = text_width(text, scale, tracking)
    draw_text(cx - w // 2, y, text, scale, color, bold, tracking)


def draw_text_right(x_right, y, text, scale, color, bold=False, tracking=0):
    w = text_width(text, scale, tracking)
    draw_text(x_right - w, y, text, scale, color, bold, tracking)


def wrap_text(text, scale, max_width):
    words = clean(text).split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons
def icon_flag(ix, iy):
    # EU-style flag: blue field, ring of gold stars, on a pole.
    rect_fill(ix + 4, iy + 2, 3, 58, INK)
    rect_fill(ix + 7, iy + 2, 52, 32, BLUE)
    cx, cy = ix + 33, iy + 18
    for k in range(8):
        ang = math.pi * 2 * k / 8
        sx = int(cx + 10 * math.cos(ang))
        sy = int(cy + 10 * math.sin(ang))
        rect_fill(sx - 1, sy - 1, 3, 3, GOLD)
    rect_fill(cx - 1, cy - 1, 3, 3, GOLD)


def icon_missile(ix, iy):
    # Rocket / missile pointing up, red fins, gold flame.
    bx, by = ix, iy
    polygon_fill([(bx + 32, by + 0), (bx + 41, by + 14), (bx + 41, by + 40),
                  (bx + 23, by + 40), (bx + 23, by + 14)], INK)
    polygon_fill([(bx + 23, by + 32), (bx + 12, by + 50), (bx + 23, by + 50)],
                 ACCENT)
    polygon_fill([(bx + 41, by + 32), (bx + 52, by + 50), (bx + 41, by + 50)],
                 ACCENT)
    polygon_fill([(bx + 27, by + 50), (bx + 37, by + 50), (bx + 32, by + 62)],
                 GOLD)
    circle_fill(bx + 32, by + 22, 4, PAPER)


def icon_mountains(ix, iy):
    # Two Andean peaks, snow caps, a red fault crack.
    polygon_fill([(ix + 0, iy + 58), (ix + 24, iy + 18), (ix + 48, iy + 58)],
                 GRAY)
    polygon_fill([(ix + 18, iy + 58), (ix + 44, iy + 8), (ix + 64, iy + 58)],
                 INK)
    polygon_fill([(ix + 44, iy + 8), (ix + 36, iy + 22), (ix + 52, iy + 22)],
                 PAPER)
    polygon_fill([(ix + 24, iy + 18), (ix + 18, iy + 28), (ix + 30, iy + 28)],
                 PAPER)
    pts = [(ix + 44, iy + 24), (ix + 40, iy + 34), (ix + 46, iy + 42),
           (ix + 41, iy + 50), (ix + 44, iy + 58)]
    for a, b in zip(pts, pts[1:]):
        line(a[0], a[1], b[0], b[1], ACCENT, 2)


def icon_shield_bug(ix, iy):
    # Shield with a computer bug inside.
    polygon_fill([(ix + 32, iy + 0), (ix + 56, iy + 9), (ix + 56, iy + 30),
                  (ix + 32, iy + 62), (ix + 8, iy + 30), (ix + 8, iy + 9)],
                 NAVY)
    cx, cy = ix + 32, iy + 34
    circle_fill(cx, cy, 9, PAPER)
    circle_fill(cx, cy - 12, 5, PAPER)
    for dx, dy, ex, ey in [(-8, -6, -16, -12), (-9, 0, -18, 0),
                           (-8, 6, -16, 12), (8, -6, 16, -12),
                           (9, 0, 18, 0), (8, 6, 16, 12)]:
        line(cx + dx, cy + dy, cx + ex, cy + ey, PAPER, 2)
    line(cx - 3, cy - 16, cx - 8, cy - 24, PAPER, 2)
    line(cx + 3, cy - 16, cx + 8, cy - 24, PAPER, 2)


# ---------------------------------------------------------------- layout
PANELS = [
    {
        "tag": "BRUSSELS - EUROPE",
        "headline": ["UK AND EU SIGN", "RESET DEAL"],
        "icon": icon_flag,
        "summary": ("Food trade, carbon and youth deals end a decade of "
                    "drift. 100,000 young people a side win 3-year stays."),
    },
    {
        "tag": "WARSAW - SECURITY",
        "headline": ["MISSILES LAND", "IN POLAND"],
        "icon": icon_missile,
        "summary": ("Two missiles and a drone fell in the southeast during "
                    "a vast barrage on Ukraine. Tusk: intentional "
                    "provocation."),
    },
    {
        "tag": "LIMA - DISASTER",
        "headline": ["6.9 QUAKE HITS", "PERU'S ANDES"],
        "icon": icon_mountains,
        "summary": ("Epicentre 34 km north of Junin, at a depth of 108 km. "
                    "Lima shook hard; no damage or casualties reported."),
    },
    {
        "tag": "WASHINGTON - AMERICA",
        "headline": ["HACKERS BREACH", "FBI AND USDA"],
        "icon": icon_shield_bug,
        "summary": ("The FBI and the Agriculture Department were hit by "
                    "cyberattacks as computer outages spread across "
                    "the US."),
    },
]


def draw_panel(x, y, w, h, panel):
    rect_outline(x, y, w, h, INK, 2)
    pad = 18
    # Shaded label band behind the section tag, stopping clear of the icon.
    rect_fill(x + 2, y + 8, w - pad - 64 - 12, 34, LIGHT)
    draw_text(x + pad, y + 14, panel["tag"], 3, ACCENT, bold=True)
    panel["icon"](x + w - pad - 64, y + 10)
    hy = y + 50
    for ln in panel["headline"]:
        draw_text(x + pad, hy, ln, 5, INK, bold=True)
        hy += 44
    line(x + pad, y + 140, x + w - pad, y + 140, INK, 2)
    sy = y + 154
    for ln in wrap_text(panel["summary"], 3, w - 2 * pad)[:5]:
        draw_text(x + pad, sy, ln, 3, INK)
        sy += 23


def build():
    # Outer frame.
    rect_outline(16, 16, W - 32, H - 32, INK, 3)

    # Masthead corner notes.
    draw_text(40, 38, "VOL. I - NO. 21", 2, GRAY)
    draw_text_right(W - 40, 38, "PRICE: ONE IMAGE", 2, GRAY)

    # Masthead.
    draw_text_centered(W // 2, 58, "WORLD NEWS", 13, INK, bold=True)
    draw_text_centered(W // 2, 162, "ALL THE WORLD IN ONE PAGE", 3, GRAY)

    # Double rule.
    rect_fill(36, 192, W - 72, 3, INK)
    rect_fill(36, 199, W - 72, 1, INK)

    # Date band.
    rect_fill(36, 212, W - 72, 116, NAVY)
    draw_text_centered(W // 2, 226, "21 NOVEMBER 2026", 9, WHITE, bold=True)
    draw_text_centered(W // 2, 296, "SATURDAY", 4, GOLD, tracking=10)

    # Dateline strip.
    rect_fill(36, 344, W - 72, 2, INK)
    draw_text_centered(W // 2, 356, "BRUSSELS - WARSAW - LIMA - WASHINGTON",
                       4, INK, bold=True)
    rect_fill(36, 394, W - 72, 2, INK)

    # News panels, 2x2.
    pw, ph = 464, 272
    xs = [36, 524]
    ys = [412, 698]
    for i, panel in enumerate(PANELS):
        draw_panel(xs[i % 2], ys[i // 2], pw, ph, panel)

    # Footer.
    draw_text_centered(W // 2, 984,
                       "COMPILED FROM WIRE AND PRESS REPORTS AROUND THE WORLD",
                       2, GRAY)


def save_png(path):
    raw = bytearray()
    row_bytes = W * 3
    for yy in range(H):
        raw.append(0)
        raw += img[yy * row_bytes:(yy + 1) * row_bytes]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


def main():
    build()
    os.makedirs("/output", exist_ok=True)
    save_png("/output/entry.png")


if __name__ == "__main__":
    main()
