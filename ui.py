"""
ui.py - glow text, neon buttons and the spin transition.

The original redrew every one of these from scratch, every frame:
`gtext()` alone stamps the string 36 times per call, and each neon button
strokes 13 rounded rectangles.  On a 60 fps loop in Python that is not
affordable, so everything here is rasterised once and cached by appearance.
"""
from __future__ import annotations

import math

import pygame

import state
from pshim import Gfx, CENTER, CORNER, color, cos, sin
import pshim

# ------------------------------------------------------------------- fonts --
_FONT_NAMES = "trebuchetms,trebuchet ms,verdana,dejavusans,freesans,arial"
_fonts: dict[int, pygame.font.Font] = {}


def font(size: int) -> pygame.font.Font:
    size = max(6, int(size))
    f = _fonts.get(size)
    if f is None:
        try:
            f = pygame.font.SysFont(_FONT_NAMES, size)
        except Exception:
            f = None
        if f is None:
            f = pygame.font.Font(None, int(size * 1.28))
        _fonts[size] = f
    return f


# --------------------------------------------------------------- glow text --
_gt_cache: dict = {}
_GT_MAX = 500


def _build_gtext(txt: str, s: int, texture, max_w=None) -> pygame.Surface:
    f = font(s)
    lines = txt.split("\n")
    lead = int(s * 1.2)
    line_surfs = [f.render(ln, True, (255, 255, 255)) for ln in lines]
    bw = max((ls.get_width() for ls in line_surfs), default=1)
    bh = lead * len(lines)

    padx = int(s / 15) + 3
    pady = int(s / 20) + 3
    surf = pygame.Surface((bw + padx * 2, bh + pady * 2), pygame.SRCALPHA)

    tinted: dict = {}

    def stamp(col, alpha, dx, dy):
        key = col[:3]
        cache = tinted.get(key)
        if cache is None:
            cache = [f.render(ln, True, key) for ln in lines]
            tinted[key] = cache
        for i, tint in enumerate(cache):
            tint.set_alpha(alpha)
            x = padx + (bw - tint.get_width()) // 2
            surf.blit(tint, (x + dx, pady + i * lead + dy))

    # 36 offset stamps of the glow colour, then the white core - exactly the
    # loop from the original gtext().
    for a in range(0, 360, 10):
        stamp(texture, texture[3], sin(a) * s / 15.0, cos(a) * s / 20.0)
    stamp((255, 255, 255, 255), 255, 0, 0)

    # The original was laid out for Trebuchet MS, which is noticeably narrower
    # than any fallback we can rely on (least of all in the browser).  Condensing
    # an over-wide block horizontally reproduces Trebuchet's proportions instead
    # of letting titles run off the canvas.
    if max_w and surf.get_width() > max_w:
        surf = pygame.transform.smoothscale(surf, (int(max_w), surf.get_height()))
    return surf


def gtext(dst, txt, x, y, s, r=0, texture=(255, 255, 255, 30), align=CENTER,
          max_w=-1):
    """Processing gtext(). `r` was declared but never used in the original."""
    txt = str(txt)
    if max_w == -1:
        max_w = (state.WIDTH - 6) if align == CENTER else None
    key = (txt, int(s), texture, align, max_w)
    surf = _gt_cache.get(key)
    if surf is None:
        if len(_gt_cache) > _GT_MAX:
            _gt_cache.clear()
        surf = _build_gtext(txt, int(s),
                            color(*texture) if len(texture) == 4 else texture,
                            max_w)
        _gt_cache[key] = surf
    w, h = surf.get_size()
    if align == CENTER:
        dst.blit(surf, (int(x - w / 2), int(y - h / 2)))
    else:  # textAlign(CORNER, CENTER) fell through to LEFT in ProcessingJS
        padx = int(s / 15) + 3
        dst.blit(surf, (int(x - padx), int(y - h / 2)))


# ------------------------------------------------------------- neon button --
def _bake_frame(w, h, tex, fade) -> pygame.Surface:
    pad = 20
    surf = pygame.Surface((int(w) + pad * 2, int(h) + pad * 2), pygame.SRCALPHA)
    g = Gfx(surf)
    pshim.use(g)
    g.translate(w / 2 + pad, h / 2 + pad)
    g.set_rect_mode(CENTER)
    g.fill(tex, fade)
    g.stroke_weight(4)
    radius = -(fade - 255) / 10.0
    for i in range(0, 360, 30):
        g.stroke(tex, 20)
        g.rect(0, 0, w + sin(i) * 5, h + sin(i) * 3, radius)
    g.stroke(tex, 160)
    g.stroke_weight(3)
    g.rect(0, 0, w, h, 5 - (fade - 255) / 10.0)
    return surf


class Button:
    """Neon menu button.  Clicking pushes a Trans that swaps scenes."""

    _frames: dict = {}

    def __init__(self, x, y, w, h, scene, txt, texturing):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.texturing = texturing
        self.txt = txt
        self.scene = scene
        self.fade_out = 255.0

    def draw(self, dst):
        bucket = int(self.fade_out) // 16
        key = (self.w, self.h, self.texturing, bucket)
        frame = Button._frames.get(key)
        if frame is None:
            frame = _bake_frame(self.w, self.h, self.texturing, bucket * 16)
            Button._frames[key] = frame
        fw, fh = frame.get_size()
        dst.blit(frame, (int(self.x - fw / 2), int(self.y - fh / 2)))
        gtext(dst, self.txt, self.x, self.y, 34, 0, self.texturing)

        if (self.x - self.w / 2 <= state.mouse_x <= self.x + self.w / 2 and
                self.y - self.h / 2 <= state.mouse_y <= self.y + self.h / 2):
            self.fade_out *= 0.7
            state.want_hand = True
            if state.clicked and len(state.tr) <= 0:
                state.tr.append(Trans(self.scene))
        else:
            self.fade_out += 6

        self.fade_out = max(0.0, min(255.0, self.fade_out))


# --------------------------------------------------------------- shop button --
class ShopBtn:
    _frames: dict = {}

    def __init__(self, x, y, w, h, kind, emerald):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.type = kind
        self.price = 5
        self.hover = 5.0
        self._emerald = emerald

    def _frame(self):
        bucket = int(self.hover)
        key = (self.w, self.h, bucket)
        f = ShopBtn._frames.get(key)
        if f is None:
            pad = 20
            surf = pygame.Surface((self.w + pad * 2, self.h + pad * 2), pygame.SRCALPHA)
            g = Gfx(surf)
            pshim.use(g)
            g.translate(self.w / 2 + pad, self.h / 2 + pad)
            g.no_fill()
            g.set_rect_mode(CENTER)
            for i in range(bucket):
                g.stroke(36, 173, 9, 50)
                g.stroke_weight(5)
                g.rect(0, 0, self.w + i, self.h + i, 10)
            ShopBtn._frames[key] = surf
            f = surf
        return f

    def draw(self, dst, admin):
        f = self._frame()
        fw, fh = f.get_size()
        dst.blit(f, (int(self.x - fw / 2), int(self.y - fh / 2)))
        gtext(dst, self.price, self.x + 10, self.y, 20, 5, color(15, 179, 0, 30), CORNER)
        pshim.image(dst, self._emerald, self.x - 25, self.y - 15, 20, 30)

        if (self.x - self.w / 2 <= state.mouse_x <= self.x + self.w / 2 and
                self.y - self.h / 2 <= state.mouse_y <= self.y + self.h / 2):
            self.hover += 1
            state.want_hand = True
            if state.clicked and admin.gems >= self.price:
                admin.gems -= self.price
                if self.type == "gamnt":
                    admin.start_amount += 100
                    self.price += 1
                elif self.type == "ggain":
                    admin.money_gain += 0.2
                    self.price += 2
        self.hover *= 0.9
        self.hover = max(3.0, min(10.0, self.hover))


# ---------------------------------------------------------------- transition --
class Trans:
    """Grabs the screen, spins it, then slides it off - then the scene swaps."""

    def __init__(self, scene):
        self.x = 0.0
        self.y = 0.0
        self.r = 0.0
        self.tim = 0.0
        self.spd = 10.0
        self.speed = 40.0
        self.pic = None
        self.grabbed = False
        self.die = False
        self.scene = scene

    def display(self, dst):
        if not self.grabbed:
            self.pic = dst.copy()
            self.grabbed = True
            self.x = state.WIDTH / 2
            self.y = state.HEIGHT / 2
            return
        dst.fill((43, 43, 43))
        pic = self.pic
        if self.r:
            pic = pygame.transform.rotate(self.pic, -self.r)
        dst.blit(pic, pic.get_rect(center=(int(self.x), int(self.y))))

    def update(self):
        self.speed *= 0.9
        self.r += self.speed
        if self.r >= 359:
            self.tim += 0.03
            if self.tim >= 0.6:
                self.x += self.spd
                self.spd += 0.5
                state.go(self.scene)
        if self.x > 900:
            self.die = True
        self.r = max(0.0, min(360.0, self.r))


# ------------------------------------------------------------------ HUD bits --
_strip_cache: dict = {}


def hud_strip(kind: str) -> pygame.Surface:
    """The stacked translucent green glow bands from Admin.display_stats()."""
    s = _strip_cache.get(kind)
    if s is not None:
        return s
    if kind == "band":
        surf = pygame.Surface((state.WIDTH, 24), pygame.SRCALPHA)
        g = Gfx(surf)
        pshim.use(g)
        g.no_stroke()
        for i in range(0, 13, 2):
            g.fill(56, 224, 47, 20)
            g.rect(0, 12 - i, state.WIDTH, 10)
    else:  # "handle" - the little scroll grip in the middle of the bottom bar
        surf = pygame.Surface((state.WIDTH // 12 + 4, 24), pygame.SRCALPHA)
        g = Gfx(surf)
        pshim.use(g)
        g.no_stroke()
        g.set_rect_mode(CENTER)
        cx = surf.get_width() / 2
        for i in range(10):
            g.fill(56, 224, 47, 30)
            g.rect(cx, 5, state.WIDTH / 12, i, 10)
            g.rect(cx, 14, state.WIDTH / 12, i, 10)
    _strip_cache[kind] = surf
    return surf


# ------------------------------------------------------------ misc helpers --
_alpha_black = None


def dim_rect(dst, x, y, w, h, alpha):
    """Cheap translucent black rect (used by the 30 grid tiles every frame)."""
    global _alpha_black
    if alpha <= 0:
        return
    if _alpha_black is None or _alpha_black.get_size() != (int(w), int(h)):
        _alpha_black = pygame.Surface((int(w), int(h)))
        _alpha_black.fill((0, 0, 0))
    _alpha_black.set_alpha(int(alpha))
    dst.blit(_alpha_black, (int(x), int(y)))


_disc_cache: dict = {}


def disc(dst, x, y, d, col, alpha):
    """Particle blob: colour-quantised circle sprites + per-surface alpha."""
    d = max(1, int(d))
    if d > 90 or alpha <= 0:
        return
    key = (d, col[0] >> 4, col[1] >> 4, col[2] >> 4)
    s = _disc_cache.get(key)
    if s is None:
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(s, (col[0], col[1], col[2], 255), (d / 2, d / 2), d / 2)
        _disc_cache[key] = s
    s.set_alpha(int(max(0, min(255, alpha))))
    dst.blit(s, (int(x - d / 2), int(y - d / 2)))
