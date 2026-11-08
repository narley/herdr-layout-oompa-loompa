#!/usr/bin/env python3
"""Pixel art for the Oompa Loompa Herdr layout's rooms, icons and backdrops, drawn in code.
The workers are SVG now: crew_svg.py.

Writes into <out>/mods/...:
  oompa-spaces/art/<room>.png                             72x72 factory rooms
  oompa-tabs/art/{files,changes,inbox}.png                40x40 icons
  oompa-chrome/sidebar.png                                536x2080 sidebar scene
  oompa-chrome/factory-map.png                            1600x1000 terminal backdrop
"""
import math, os, random, sys
from PIL import Image

OUT = sys.argv[1]

# ── palette ──────────────────────────────────────────────────────────────────
C = dict(
    ink=(26, 13, 8), skin=(240, 134, 44), skin_d=(198, 98, 28), skin_l=(255, 170, 90),
    hair=(70, 178, 74), hair_d=(36, 120, 48), hair_l=(140, 222, 110),
    brow=(255, 252, 240), eye=(26, 13, 8), mouth=(110, 40, 20),
    shirt=(98, 56, 32), shirt_d=(66, 36, 20), white=(250, 244, 232), white_d=(214, 202, 184),
    shoe=(70, 40, 24), shoe_l=(110, 66, 40), button=(150, 110, 70),
    choc=(92, 50, 28), choc_d=(58, 30, 16), choc_l=(140, 82, 46), cream=(255, 236, 200),
    gold=(255, 201, 60), gold_d=(200, 140, 30), gold_l=(255, 236, 140),
    pink=(255, 122, 200), pink_d=(205, 70, 150), pink_l=(255, 180, 228),
    mint=(95, 212, 196), cherry=(255, 90, 110), blue=(110, 140, 255), purple=(170, 120, 255),
    wood=(170, 110, 60), wood_d=(120, 72, 36), steel=(170, 170, 190), steel_d=(110, 110, 130),
    nut=(180, 120, 60), nut_d=(120, 76, 36),
)
T = (0, 0, 0, 0)


class Canvas:
    def __init__(self, w, h, bg=T):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w, h), bg)
        self.px = self.img.load()

    def p(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[x, y] = c + (255,) if len(c) == 3 else c

    def rect(self, x0, y0, x1, y1, c):  # inclusive
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.p(x, y, c)

    def line(self, x0, y0, x1, y1, c, w=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n + 1):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if w == 1:
                self.p(x, y, c)
            else:
                self.rect(round(x) - (w - 1) // 2, round(y) - (w - 1) // 2, round(x) + w // 2, round(y) + w // 2, c)

    def disc(self, cx, cy, r, c):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.3:
                    self.p(x, y, c)

    def ring(self, cx, cy, r, c):
        for a in range(0, 360, 4):
            self.p(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), c)

    def get(self, x, y):
        return self.px[x, y] if 0 <= x < self.w and 0 <= y < self.h else T

    def outline(self, color=C["ink"]):
        src = self.img.copy().load()
        for y in range(self.h):
            for x in range(self.w):
                if src[x, y][3]:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and src[nx, ny][3] and src[nx, ny][:3] != color:
                        self.px[x, y] = color + (255,)
                        break

    def paste(self, other, x=0, y=0):
        self.img.alpha_composite(other.img, (x, y))

    def scaled(self, k):
        return self.img.resize((self.w * k, self.h * k), Image.NEAREST)


# ── factory rooms for spaces (36x36 at 2x) ────────────────────────────────────
def room(kind):
    cv = Canvas(36, 36)
    rnd = random.Random(kind)
    if kind == "waterfall":      # the chocolate room: green candy meadow, river and fall
        cv.rect(0, 0, 35, 35, (74, 20, 52))
        for _ in range(14): cv.p(rnd.randint(0, 35), rnd.randint(0, 12), C["gold_l"])
        cv.rect(0, 14, 35, 35, (60, 150, 70)); cv.rect(0, 14, 35, 15, C["hair_l"])
        cv.rect(14, 2, 21, 30, C["choc"]); cv.rect(15, 2, 16, 30, C["choc_l"]); cv.rect(19, 2, 19, 30, C["choc_d"])
        cv.rect(4, 28, 33, 35, C["choc"]); cv.rect(4, 28, 33, 28, C["choc_l"])
        for x in range(6, 32, 4): cv.p(x, 31, C["choc_l"])
        for x, h, col in ((4, 8, "pink"), (28, 10, "gold"), (9, 6, "mint")):
            cv.line(x, 26, x, 26 - h, C["white"], 1); cv.disc(x, 26 - h - 2, 2.2, C[col])
        cv.rect(12, 24, 23, 27, C["cream"])  # foam
    elif kind == "factory":      # the brick factory with candy-coloured smoke
        cv.rect(0, 0, 35, 35, (58, 16, 46))
        for _ in range(10): cv.p(rnd.randint(0, 35), rnd.randint(0, 14), C["gold_l"])
        cv.rect(3, 16, 32, 35, (150, 62, 48))
        for y in range(17, 35, 3):
            for x in range(3 + (y // 3 % 2) * 2, 33, 4): cv.p(x, y, (110, 40, 32))
        for cx in (7, 15, 26):
            cv.rect(cx, 6, cx + 3, 16, (120, 50, 40)); cv.rect(cx, 6, cx + 3, 6, (90, 36, 30))
        for i, (cx, col) in enumerate(((8, "pink"), (16, "mint"), (27, "purple"))):
            cv.disc(cx + 1, 3, 2, C[col]); cv.disc(cx + 3, 1, 1.5, C[col])
        for x in (6, 13, 20, 27):
            cv.rect(x, 21, x + 3, 25, C["gold"]); cv.rect(x, 21, x + 3, 21, C["gold_l"])
        cv.rect(15, 28, 20, 35, C["choc_d"]); cv.rect(15, 28, 20, 28, C["gold_d"])
    elif kind == "inventing":    # bubbling flasks and a gobstopper machine
        cv.rect(0, 0, 35, 35, (22, 52, 58))
        cv.rect(0, 26, 35, 35, C["steel_d"]); cv.rect(0, 26, 35, 26, C["steel"])
        cv.rect(16, 6, 31, 25, C["steel"]); cv.rect(17, 7, 30, 24, (90, 96, 130))
        cv.disc(23.5, 14, 4, C["purple"]); cv.disc(22.5, 13, 1.5, C["pink_l"])
        for i, x in enumerate((19, 22, 25, 28)): cv.p(x, 21, (C["cherry"], C["gold"], C["mint"], C["pink"])[i])
        cv.line(23, 2, 23, 6, C["steel"], 1); cv.disc(23, 2, 1, C["gold"])
        for x, col in ((4, "mint"), (10, "pink")):
            cv.rect(x, 14, x + 1, 19, C["white"]); cv.disc(x + 0.5, 22, 3, C[col]); cv.p(x - 1, 21, C["white"])
            cv.p(x + rnd.randint(-1, 2), 11, C[col]); cv.p(x + rnd.randint(-1, 2), 8, C[col])
        cv.rect(1, 29, 12, 34, C["choc_d"]); cv.rect(2, 30, 11, 33, C["choc"])
    else:                        # orchard: candy canes, lollipops and gumdrops
        cv.rect(0, 0, 35, 35, (70, 22, 58))
        for _ in range(12): cv.p(rnd.randint(0, 35), rnd.randint(0, 16), C["gold_l"])
        cv.rect(0, 25, 35, 35, (70, 160, 80)); cv.rect(0, 25, 35, 25, C["hair_l"])
        for x in (5, 25):
            for y in range(8, 30):
                cv.rect(x, y, x + 1, y, C["white"] if (y // 2) % 2 else C["cherry"])
            cv.rect(x + 2, 6, x + 4, 7, C["cherry"]); cv.rect(x + 1, 6, x + 1, 8, C["white"]); cv.p(x + 4, 8, C["white"])
        cv.line(16, 29, 16, 15, C["white"], 1); cv.disc(16, 12, 4, C["pink"]); cv.ring(16, 12, 2, C["pink_l"])
        for x, col in ((10, "mint"), (21, "gold"), (31, "purple")):
            cv.disc(x, 30, 2.5, C[col]); cv.p(x - 1, 29, C["white"])
    cv.outline()
    big = Canvas(36, 36); big.paste(cv)
    return big.scaled(2)


# ── tab icons (20x20 at 2x) ───────────────────────────────────────────────────
def icon(kind):
    cv = Canvas(20, 20)
    if kind == "files":          # a recipe book
        cv.rect(3, 3, 16, 17, C["cherry"]); cv.rect(4, 4, 15, 16, (210, 70, 80))
        cv.rect(3, 3, 4, 17, (150, 40, 50)); cv.rect(15, 5, 16, 16, C["cream"])
        cv.rect(7, 7, 12, 7, C["gold"]); cv.rect(7, 9, 12, 9, C["gold"]); cv.disc(9.5, 13, 1.5, C["gold"])
    elif kind == "changes":      # a chocolate bar half unwrapped
        cv.rect(4, 2, 15, 9, C["choc"])
        for x in (4, 8, 12):
            cv.rect(x, 2, x + 2, 4, C["choc_l"]); cv.rect(x, 6, x + 2, 8, C["choc_l"])
        cv.rect(4, 10, 15, 17, C["gold"]); cv.rect(4, 10, 15, 10, C["gold_l"]); cv.rect(4, 13, 15, 14, C["cherry"])
    else:                        # inbox: the golden ticket
        cv.rect(1, 5, 18, 14, C["gold"]); cv.rect(1, 5, 18, 5, C["gold_l"])
        cv.rect(3, 7, 16, 12, C["gold_d"]); cv.rect(4, 8, 15, 11, C["gold"])
        cv.rect(6, 9, 13, 9, C["choc"]); cv.rect(7, 10, 12, 10, C["choc"])
        for x in (1, 18): cv.p(x, 9, T); cv.p(x, 10, T)
    cv.outline()
    return cv.scaled(2)


# ── sidebar scene (134x520 at 4x), dark so text reads over it ─────────────────
def dim(c, k):
    return tuple(int(v * k) for v in c)


def _rays(cv, cx, cy, w, h, n, ca, cb, fade):
    """A sunburst: n alternating rays around (cx, cy), fading with distance."""
    for y in range(h):
        for x in range(w):
            ang = math.atan2(y - cy, x - cx)
            k = int((ang + math.pi) / (2 * math.pi / n)) % 2
            d = math.hypot(x - cx, y - cy)
            f = max(0.0, 1 - d / fade)
            base = cv.get(x, y)[:3]
            col = ca if k else cb
            cv.p(x, y, tuple(int(base[i] + (col[i] - base[i]) * f) for i in range(3)))


def _cloud(cv, x, y, s, col):
    for dx, dy, r in ((0, 0, 1.0), (1.1, 0.25, 0.8), (-1.0, 0.3, 0.75), (0.45, -0.55, 0.7), (-0.45, -0.45, 0.6)):
        cv.disc(x + dx * s, y + dy * s, r * s, col)


def _curtain(cv, x0, x1, h, col, side):
    """A velvet drape with folds, gathered toward its outer edge."""
    for x in range(x0, x1 + 1):
        t = (x - x0) / max(1, x1 - x0)
        if side == "right":
            t = 1 - t
        bottom = int(h * (0.35 + 0.65 * (1 - t) ** 0.6))
        fold = 0.78 + 0.22 * math.cos(x * 0.9)
        cv.rect(x, 0, x, bottom, tuple(int(v * fold) for v in col))
        cv.p(x, bottom, (190, 140, 60))


def sidebar():
    """Velvet curtains over a teal and cream sunburst, cotton-candy clouds, candy below."""
    w, h = 134, 520
    cv = Canvas(w, h, (60, 16, 40, 255))
    rnd = random.Random(7)
    for y in range(h):   # raspberry at the top to chocolate plum below
        t = y / h
        cv.rect(0, y, w - 1, y, (int(66 - 34 * t), int(16 - 2 * t), int(44 - 20 * t)))
    _rays(cv, 67, 170, w, 360, 18, (44, 96, 92), (110, 84, 70), 230)
    for _ in range(9):
        _cloud(cv, rnd.randint(-6, w + 6), rnd.randint(150, 330), rnd.randint(6, 11), rnd.choice(((150, 76, 110), (170, 96, 128), (128, 60, 96))))
    _curtain(cv, 0, 34, 260, (124, 22, 58), "left")
    _curtain(cv, w - 35, w - 1, 260, (124, 22, 58), "right")
    for x in range(0, w, 2):   # the swag along the top, gold fringe beneath
        sag = int(10 + 6 * math.sin(x / w * math.pi * 3) ** 2)
        cv.rect(x, 0, x + 1, sag, (110, 18, 50))
        cv.p(x, sag + 1, (200, 150, 64))
    cv.rect(0, 360, w - 1, h - 1, (40, 18, 22))   # a chocolate floor
    for y in range(362, h, 6):
        cv.rect(0, y, w - 1, y, (48, 22, 26))
    for _ in range(18):   # swirl lollipops and gumdrops, dim so text reads
        x, y = rnd.randint(4, w - 6), rnd.randint(330, h - 12)
        if rnd.random() < 0.6:
            cv.line(x, y, x, y - 9, (150, 130, 120))
            c = rnd.choice(((180, 70, 110), (60, 150, 140), (200, 160, 70)))
            cv.disc(x, y - 12, 3.2, c); cv.ring(x, y - 12, 1.6, (230, 210, 190))
        else:
            cv.disc(x, y, 2.4, rnd.choice(((150, 60, 100), (60, 130, 120), (180, 140, 60))))
    return cv.scaled(4)


def factory_map():
    """The terminal backdrop: a dark plum stage, a faint sunburst, clouds and candy, low contrast."""
    w, h = 400, 250
    cv = Canvas(w, h, (32, 12, 24, 255))
    rnd = random.Random(11)
    _rays(cv, 200, 300, w, h, 28, (34, 50, 52), (52, 30, 40), 420)
    for _ in range(14):
        _cloud(cv, rnd.randint(0, w), rnd.randint(30, 200), rnd.randint(8, 16), rnd.choice(((56, 24, 44), (62, 28, 50))))
    for x in range(0, w, 3):   # a velvet valance and fringe along the top
        sag = int(9 + 5 * math.sin(x / w * math.pi * 6) ** 2)
        cv.rect(x, 0, x + 2, sag, (64, 14, 36))
        cv.p(x + 1, sag + 1, (96, 72, 34))
    for _ in range(26):   # lollipops and gumdrops on the stage floor
        x, y = rnd.randint(0, w), rnd.randint(150, h - 4)
        if rnd.random() < 0.5:
            cv.line(x, y, x, y - 12, (60, 46, 46)); cv.disc(x, y - 16, 5, rnd.choice(((70, 28, 52), (34, 62, 60), (72, 58, 30))))
        else:
            cv.disc(x, y, 4, rnd.choice(((60, 26, 46), (32, 56, 54), (66, 52, 28))))
    return cv.scaled(4)


def main():
    m = lambda *p: os.path.join(OUT, "mods", *p)
    for d in ("oompa-spaces/art", "oompa-tabs/art", "oompa-chrome"):
        os.makedirs(m(d), exist_ok=True)
    for r in ("waterfall", "factory", "inventing", "orchard"):
        room(r).save(m("oompa-spaces/art", f"{r}.png"))
    for k in ("files", "changes", "inbox"):
        icon(k).save(m("oompa-tabs/art", f"{k}.png"))
    sidebar().save(m("oompa-chrome", "sidebar-velvet.png"), optimize=True)
    factory_map().save(m("oompa-chrome", "stage-map.png"), optimize=True)


main()
