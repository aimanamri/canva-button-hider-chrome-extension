#!/usr/bin/env python3
"""Generate the pixel-art assets: extension icons and README GIFs.

    python3 -m venv .venv && .venv/bin/pip install pillow
    .venv/bin/python scripts/make_art.py

Everything is drawn on a tiny grid and scaled with nearest-neighbour, so the
art stays crisp. Output: extension/icons/*.png and docs/*.gif
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "extension" / "icons"
DOCS = ROOT / "docs"

# ---- palette -------------------------------------------------------------
BG = (21, 18, 46)
PURPLE = (108, 76, 245)
PURPLE_HI = (141, 115, 255)
PURPLE_LO = (72, 48, 190)
WHITE = (255, 255, 255)
LAV = (196, 190, 245)
YELLOW = (255, 201, 51)
YELLOW_HI = (255, 236, 150)
STAR = (70, 64, 120)
OFF = (74, 69, 128)
GREEN = (98, 224, 165)

# ---- 5x5 pixel font ------------------------------------------------------
FONT = {
    "A": ".XXX.|X...X|XXXXX|X...X|X...X",
    "B": "XXXX.|X...X|XXXX.|X...X|XXXX.",
    "C": ".XXXX|X....|X....|X....|.XXXX",
    "D": "XXXX.|X...X|X...X|X...X|XXXX.",
    "E": "XXXXX|X....|XXXX.|X....|XXXXX",
    "F": "XXXXX|X....|XXXX.|X....|X....",
    "H": "X...X|X...X|XXXXX|X...X|X...X",
    "I": "XXXXX|..X..|..X..|..X..|XXXXX",
    "L": "X....|X....|X....|X....|XXXXX",
    "N": "X...X|XX..X|X.X.X|X..XX|X...X",
    "O": ".XXX.|X...X|X...X|X...X|.XXX.",
    "R": "XXXX.|X...X|XXXX.|X..X.|X...X",
    "S": ".XXXX|X....|.XXX.|....X|XXXX.",
    "T": "XXXXX|..X..|..X..|..X..|..X..",
    "U": "X...X|X...X|X...X|X...X|.XXX.",
    "V": "X...X|X...X|X...X|.X.X.|..X..",
    " ": "...|...|...|...|...",
}


def text_width(s):
    return sum(len(FONT[c].split("|")[0]) + 1 for c in s) - 1


def draw_text(d, x, y, s, color):
    """Draw text on a grid-sized ImageDraw. Returns the pixel list too."""
    pts = []
    for c in s:
        rows = FONT[c].split("|")
        for ry, row in enumerate(rows):
            for rx, ch in enumerate(row):
                if ch == "X":
                    d.point((x + rx, y + ry), fill=color)
                    pts.append((x + rx, y + ry))
        x += len(rows[0]) + 1
    return pts


def scale(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


def save_gif(frames, durations, path):
    pal = [f.quantize(colors=24, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
           for f in frames]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=durations,
                loop=0, disposal=2, optimize=False)
    print("wrote", path.relative_to(ROOT), f"{path.stat().st_size // 1024} KB")


# ---- icon ----------------------------------------------------------------
ICON = [
    ".HHHHHHHHHHHHHH.",
    "HPPPPPPPPPPPPPPL",
    "HPPPPPPPPPPPPPPL",
    "HPPPPPPPPPPPPWWL",
    "HPPPPPPPPPPWWWWL",
    "HPPPPPPPPWWWWWWL",
    "HPPPPPPWWWWWWWWL",
    "HPPPWWWWWWWWWWPL",
    "HPPPPPWWWWWWWPPL",
    "HPPPPPPPAWWWPPPL",
    "HPPPPPPPPAAYYPPL",
    "HPPPPPPPPPYYYPPL",
    "HPPPPPPPPYYYYYPL",
    "HPPPPPPPPPPYYPPL",
    "LPPPPPPPPPPYPPPL",
    ".LLLLLLLLLLLLLL.",
]
ICON_COLORS = {"P": PURPLE, "H": PURPLE_HI, "L": PURPLE_LO, "W": WHITE, "Y": YELLOW, "A": LAV}


def make_icons():
    ICONS.mkdir(parents=True, exist_ok=True)
    base = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(ICON):
        for x, ch in enumerate(row):
            if ch in ICON_COLORS:
                col = ICON_COLORS[ch]
                base.putpixel((x, y), col + (255,))
    for size in (16, 32, 48, 128):
        img = base if size == 16 else base.resize((size, size), Image.NEAREST)
        img.save(ICONS / f"icon{size}.png")
        print("wrote", f"extension/icons/icon{size}.png")


# ---- shared drawing helpers ------------------------------------------------
def stars(d, w, h, seed, t=0):
    rnd = random.Random(seed)
    for _ in range(int(w * h / 90)):
        x, y = rnd.randrange(w), rnd.randrange(h)
        phase = rnd.randrange(6)
        if (t + phase) % 6 < 4:
            d.point((x, y), fill=STAR)


def button(d, x, y, label, bg=PURPLE):
    w = text_width(label) + 10
    d.rectangle((x, y, x + w - 1, y + 12), fill=bg)
    d.rectangle((x, y + 11, x + w - 1, y + 12), fill=PURPLE_LO)
    d.point((x, y), fill=BG)
    d.point((x + w - 1, y), fill=BG)
    pts = draw_text(d, x + 5, y + 3, label, WHITE)
    return w, pts


def bolt(d, cx, y0, y1, color=YELLOW, core=YELLOW_HI):
    """Zig-zag lightning bolt from y0 down to y1 around column cx."""
    x, y, dx = cx, y0, 3
    while y < y1:
        d.rectangle((x, y, x + 2, y + 2), fill=color)
        d.point((x + 1, y + 1), fill=core)
        y += 3
        x += dx
        dx = -dx


# ---- hero banner ---------------------------------------------------------
def make_hero():
    W, H, K = 160, 60, 5
    title = "CANVA BUTTON HIDER"
    label = "SEND TO TEACHER"
    rnd = random.Random(7)
    bw = text_width(label) + 10
    bx, by = (W - bw) // 2, 34
    probe = Image.new("RGB", (W, H))
    _, btn_pts = button(ImageDraw.Draw(probe), bx, by, label)
    order = list(range(len(btn_pts)))
    rnd.shuffle(order)
    rank = {btn_pts[i]: r for r, i in enumerate(order)}
    # include the button body pixels so the whole thing dissolves
    body = [(x, y) for x in range(bx, bx + bw) for y in range(by, by + 13)]
    rnd.shuffle(body)
    brank = {p: r for r, p in enumerate(body)}

    frames, durs = [], []
    t = 0

    def frame(draw_fn, dur):
        nonlocal t
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        stars(d, W, H, 3, t)
        t += 1
        d.rectangle((0, 0, W, 0), fill=BG)
        draw_text(d, (W - text_width(title)) // 2, 8, title, WHITE)
        draw_fn(img, d)
        frames.append(scale(img, K))
        durs.append(dur)

    # 1. button sits there smugly
    for _ in range(6):
        frame(lambda i, d: button(d, bx, by, label), 120)
    # 2. bolt charges and strikes
    for n in range(3):
        def strike(i, d, n=n):
            button(d, bx, by, label, PURPLE_HI if n % 2 else PURPLE)
            bolt(d, W // 2 - 1, 18, by + 3 - (2 - n) * 6 if n < 2 else by + 3)
        frame(strike, 70)
    # 3. flash
    def flash(i, d):
        d.rectangle((0, 0, W, H), fill=WHITE)
    frame(flash, 60)
    # 4. dissolve into sparks
    steps = 10
    for s in range(steps + 1):
        frac = s / steps
        def dissolve(i, d, frac=frac):
            cut = int(frac * len(body))
            for p, r in brank.items():
                if r >= cut:
                    d.point(p, fill=PURPLE if p[1] < by + 11 else PURPLE_LO)
            for p in btn_pts:
                if brank[p] >= cut:
                    d.point(p, fill=WHITE)
            for p, r in brank.items():
                if cut - 14 <= r < cut and r % 3 == 0:
                    off = (cut - r) // 2
                    d.point((p[0], max(0, p[1] - off - 1)), fill=YELLOW)
        frame(dissolve, 60)
    # 5. victory text
    msg = "HIDDEN"
    for n in range(8):
        def win(i, d, n=n):
            col = GREEN if n % 4 < 3 else WHITE
            draw_text(d, (W - text_width(msg)) // 2, by + 3, msg, col)
        frame(win, 140)
    # 6. brief pause before looping back
    frame(lambda i, d: None, 300)
    save_gif(frames, durs, DOCS / "hero.gif")


# ---- toggle demo ---------------------------------------------------------
def make_demo():
    W, H, K = 120, 70, 5
    rnd = random.Random(11)
    frames, durs = [], []

    px, py, pw, ph = 20, 6, 80, 58  # popup panel

    def base(d, knob_t, on_label):
        d.rectangle((px, py, px + pw - 1, py + ph - 1), fill=(30, 26, 66))
        d.rectangle((px, py, px + pw - 1, py), fill=PURPLE_HI)
        draw_text(d, px + 6, py + 6, "HIDE", WHITE)
        # switch
        sx, sy = px + pw - 28, py + 5
        track = PURPLE if knob_t > 0.5 else OFF
        d.rectangle((sx, sy, sx + 21, sy + 9), fill=track)
        kx = sx + 1 + round(knob_t * 12)
        d.rectangle((kx, sy + 1, kx + 7, sy + 8), fill=WHITE)
        draw_text(d, px + 6, py + 14, on_label, YELLOW if on_label == "ON" else LAV)

    def mock(d, alpha_cols, spark=0):
        d.rectangle((px + 6, py + 26, px + pw - 7, py + ph - 7), fill=(38, 34, 79))
        d.rectangle((px + 9, py + 31, px + 18, py + 33), fill=OFF)
        d.rectangle((px + 22, py + 31, px + 31, py + 33), fill=OFF)
        bx0, by0 = px + 34, py + 29
        label_w = 36
        for cx in range(alpha_cols):
            pass
        d.rectangle((px + 6, py + 40, px + pw - 7, py + 40), fill=OFF)
        return bx0, by0, label_w

    def render(knob_t, label, dissolve, bolt_on, flash):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        stars(d, W, H, 5)
        base(d, knob_t, label)
        bx0, by0, lw = mock(d, 0)
        # the Send button on the mock page toolbar
        bw2, bh2 = 40, 11
        rx, ry = px + pw - 7 - bw2 - 3, py + 29
        pts = [(x, y) for x in range(rx, rx + bw2) for y in range(ry, ry + bh2)]
        cut = int(dissolve * len(pts))
        order = pts[:]
        random.Random(3).shuffle(order)
        gone = set(order[:cut])
        for p in pts:
            if p not in gone:
                bar = ry + 4 <= p[1] <= ry + 5 and rx + 5 <= p[0] <= rx + bw2 - 6
                d.point(p, fill=WHITE if bar else (PURPLE if p[1] < ry + 9 else PURPLE_LO))
        for i, p in enumerate(order[max(0, cut - 20):cut]):
            if i % 2 == 0 and 0 < dissolve < 1:
                d.point((p[0], p[1] - 2 - i // 4), fill=YELLOW)
        if bolt_on:
            bolt(d, rx + bw2 // 2 - 1, py + 18, ry + 3)
        if flash:
            d.rectangle((rx - 1, ry - 1, rx + bw2, ry + bh2), fill=WHITE)
        return scale(img, K)

    def add(img, dur):
        frames.append(img)
        durs.append(dur)

    for _ in range(5):
        add(render(0, "OFF", 0, False, False), 160)
    for i in range(1, 5):                      # knob slides
        add(render(i / 4, "OFF" if i < 3 else "ON", 0, False, False), 60)
    add(render(1, "ON", 0, True, False), 70)
    add(render(1, "ON", 0, True, True), 60)
    for i in range(1, 9):                      # dissolve
        add(render(1, "ON", i / 8, False, False), 55)
    for _ in range(9):
        add(render(1, "ON", 1, False, False), 160)
    for i in range(3, -1, -1):                 # back off, button returns
        add(render(i / 3, "OFF", 0, False, False), 70)
    save_gif(frames, durs, DOCS / "toggle.gif")


if __name__ == "__main__":
    DOCS.mkdir(exist_ok=True)
    make_icons()
    make_hero()
    make_demo()
