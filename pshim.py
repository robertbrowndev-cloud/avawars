"""
pshim.py - a small Processing.js (Khan Academy flavour) compatibility layer
drawn onto pygame Surfaces.

Why this exists
---------------
AVAWARS' artwork is ~2000 lines of `beginShape/bezierVertex/endShape` calls.
Rewriting that art by hand into pygame polygons would be error prone and would
lose the original's intent.  Instead we implement just enough of Processing's
immediate-mode API that the art transcribes almost line-for-line, then we bake
the result to a Surface exactly once (see assets.py).

Important fidelity notes
------------------------
*  Khan Academy's ProcessingJS runs in DEGREES: `rotate()`, `arc()`, `sin()`,
   `cos()` all take degrees.  This shim does too.
*  ProcessingJS buffers `vertex()` calls and only applies the CTM at
   `endShape()` time.  The original art relies on this - `Vortantree` calls
   `translate()` *inside* a `beginShape()` block and expects the whole shape to
   move.  We replicate that: raw vertices in, transform applied at end_shape.
*  `pygame.draw.*` writes colours verbatim instead of alpha-blending them, so
   every translucent shape is drawn to a bbox-sized scratch surface and blitted
   (blit does correct source-over compositing).  Bbox-limiting keeps this cheap.
*  Antialiasing comes from supersampling the whole bake (see assets.py), not
   from gfxdraw - `pygame.gfxdraw` is not reliably available in the pygbag /
   WebAssembly build.
"""
from __future__ import annotations

import math
import random as _random

import pygame

# ---------------------------------------------------------------- constants --
CORNER = "CORNER"
CORNERS = "CORNERS"
CENTER = "CENTER"
RADIUS = "RADIUS"
LEFT = "LEFT"
RIGHT = "RIGHT"
TOP = "TOP"
BOTTOM = "BOTTOM"
BASELINE = "BASELINE"
CLOSE = "CLOSE"
BLUR = "BLUR"

_DEG = 0.017453292519943295


# ------------------------------------------------------------ math helpers --
def sin(deg: float) -> float:
    return math.sin(deg * _DEG)


def cos(deg: float) -> float:
    return math.cos(deg * _DEG)


def constrain(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


def dist(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def rnd(a=1.0, b=None):
    """Processing random(): random(hi) or random(lo, hi)."""
    if b is None:
        a, b = 0.0, a
    return _random.uniform(a, b)


def p_round(v):
    """JS Math.round: halves go up, not to-even like Python's round()."""
    return int(math.floor(v + 0.5))


def color(*a):
    """Processing color(): gray | gray,alpha | r,g,b | r,g,b,a | rgba,alpha."""
    n = len(a)
    if n == 1:
        v = a[0]
        if isinstance(v, (tuple, list)):
            return (int(v[0]), int(v[1]), int(v[2]), 255 if len(v) < 4 else int(v[3]))
        return (int(v), int(v), int(v), 255)
    if n == 2:
        v, al = a
        if isinstance(v, (tuple, list)):
            return (int(v[0]), int(v[1]), int(v[2]), int(constrain(al, 0, 255)))
        return (int(v), int(v), int(v), int(constrain(al, 0, 255)))
    if n == 3:
        return (int(a[0]), int(a[1]), int(a[2]), 255)
    return (int(a[0]), int(a[1]), int(a[2]), int(constrain(a[3], 0, 255)))


# ------------------------------------------------------------ curve helpers --
def _bezier_points(p0, p1, p2, p3, n):
    out = []
    for i in range(1, n + 1):
        t = i / n
        mt = 1.0 - t
        a = mt * mt * mt
        b = 3 * mt * mt * t
        c = 3 * mt * t * t
        d = t * t * t
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def _catmull_points(p0, p1, p2, p3, n):
    """Catmull-Rom == Processing's curveVertex() at the default tightness of 0."""
    out = []
    for i in range(1, n + 1):
        t = i / n
        t2 = t * t
        t3 = t2 * t
        out.append((
            0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                   + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                   + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
            0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                   + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                   + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3),
        ))
    return out


def _segments_for(p0, p3, extra=0.0):
    """Adaptive tessellation: more segments for longer curves."""
    d = math.hypot(p3[0] - p0[0], p3[1] - p0[1]) + extra
    return int(constrain(d / 4.0, 6, 48))


# --------------------------------------------------------------------- Gfx --
class Gfx:
    """An immediate-mode Processing-ish drawing context bound to one Surface."""

    def __init__(self, surface: pygame.Surface, scale: float = 1.0):
        self.surf = surface
        self.w, self.h = surface.get_size()
        self.m = [scale, 0.0, 0.0, scale, 0.0, 0.0]
        self._mstack = []
        self._sstack = []
        self.fill_c = (255, 255, 255, 255)
        self.stroke_c = (0, 0, 0, 255)
        self.do_fill = True
        self.do_stroke = True
        self.weight = 1.0
        self.rect_mode = CORNER
        self.ellipse_mode = CENTER
        self._ops = None

    # ------------------------------------------------------------ transform --
    def pt(self, x, y):
        a, b, c, d, e, f = self.m
        return (a * x + c * y + e, b * x + d * y + f)

    def push_matrix(self):
        self._mstack.append(list(self.m))

    def pop_matrix(self):
        if self._mstack:
            self.m = self._mstack.pop()

    def translate(self, tx, ty):
        if tx is None or ty is None:
            return
        a, b, c, d, e, f = self.m
        self.m[4] = e + a * tx + c * ty
        self.m[5] = f + b * tx + d * ty

    def scale(self, sx, sy=None):
        if sx is None:
            return
        if sy is None:
            sy = sx
        self.m[0] *= sx
        self.m[1] *= sx
        self.m[2] *= sy
        self.m[3] *= sy

    def rotate(self, deg):
        if not deg:
            return
        co, si = cos(deg), sin(deg)
        a, b, c, d, e, f = self.m
        self.m = [a * co + c * si, b * co + d * si,
                  -a * si + c * co, -b * si + d * co, e, f]

    def _mscale(self):
        a, b, c, d = self.m[0], self.m[1], self.m[2], self.m[3]
        return math.sqrt(abs(a * d - b * c)) or 1.0

    # ---------------------------------------------------------------- style --
    def push_style(self):
        self._sstack.append((self.fill_c, self.stroke_c, self.do_fill,
                             self.do_stroke, self.weight,
                             self.rect_mode, self.ellipse_mode))

    def pop_style(self):
        if self._sstack:
            (self.fill_c, self.stroke_c, self.do_fill, self.do_stroke,
             self.weight, self.rect_mode, self.ellipse_mode) = self._sstack.pop()

    def fill(self, *a):
        self.fill_c = color(*a)
        self.do_fill = True

    def no_fill(self):
        self.do_fill = False

    def stroke(self, *a):
        self.stroke_c = color(*a)
        self.do_stroke = True

    def no_stroke(self):
        self.do_stroke = False

    def stroke_weight(self, w):
        self.weight = w

    def set_rect_mode(self, m):
        self.rect_mode = m

    def set_ellipse_mode(self, m):
        self.ellipse_mode = m

    def background(self, *a):
        self.surf.fill(color(*a))

    # ------------------------------------------------------------ rasterise --
    def _fill_poly(self, pts, col=None):
        if len(pts) < 3:
            return
        col = col or self.fill_c
        r, g, b, al = col
        ip = [(int(round(x)), int(round(y))) for x, y in pts]
        if al >= 254:
            pygame.draw.polygon(self.surf, (r, g, b, 255), ip)
            return
        if al <= 0:
            return
        x0 = max(min(p[0] for p in ip), 0)
        y0 = max(min(p[1] for p in ip), 0)
        x1 = min(max(p[0] for p in ip), self.w - 1)
        y1 = min(max(p[1] for p in ip), self.h - 1)
        bw, bh = x1 - x0 + 1, y1 - y0 + 1
        if bw <= 0 or bh <= 0:
            return
        tmp = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.polygon(tmp, (r, g, b, al), [(p[0] - x0, p[1] - y0) for p in ip])
        self.surf.blit(tmp, (x0, y0))

    def _stroke_path(self, pts, closed, col=None, weight=None):
        if len(pts) < 2:
            return
        col = col or self.stroke_c
        wpx = max(1, int(round((self.weight if weight is None else weight) * self._mscale())))
        r, g, b, al = col
        ip = [(int(round(x)), int(round(y))) for x, y in pts]
        if al >= 254:
            pygame.draw.lines(self.surf, (r, g, b, 255), closed, ip, wpx)
            return
        if al <= 0:
            return
        pad = wpx + 2
        x0 = max(min(p[0] for p in ip) - pad, 0)
        y0 = max(min(p[1] for p in ip) - pad, 0)
        x1 = min(max(p[0] for p in ip) + pad, self.w - 1)
        y1 = min(max(p[1] for p in ip) + pad, self.h - 1)
        bw, bh = x1 - x0 + 1, y1 - y0 + 1
        if bw <= 0 or bh <= 0:
            return
        tmp = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.lines(tmp, (r, g, b, al), closed,
                          [(p[0] - x0, p[1] - y0) for p in ip], wpx)
        self.surf.blit(tmp, (x0, y0))

    def _emit(self, pts, closed=True):
        """Fill (always closed) then stroke (closed only if asked)."""
        if self.do_fill:
            self._fill_poly(pts)
        if self.do_stroke:
            self._stroke_path(pts, closed)

    # ------------------------------------------------------------- vertices --
    def begin_shape(self):
        self._ops = []

    def vertex(self, x, y):
        self._ops.append(("v", x, y))

    def bezier_vertex(self, cx1, cy1, cx2, cy2, x, y):
        self._ops.append(("b", cx1, cy1, cx2, cy2, x, y))

    def curve_vertex(self, x, y):
        self._ops.append(("c", x, y))

    def end_shape(self, mode=None):
        ops, self._ops = self._ops, None
        if not ops:
            return
        # transform every control point up-front (ProcessingJS applies the CTM
        # at endShape() time, not at vertex() time)
        t = []
        for op in ops:
            if op[0] == "b":
                t.append(("b", self.pt(op[1], op[2]), self.pt(op[3], op[4]), self.pt(op[5], op[6])))
            else:
                t.append((op[0], self.pt(op[1], op[2])))

        pts = []
        if any(op[0] == "c" for op in t):
            # ProcessingJS: curveVertex() sets isCurve, and endShape() then
            # renders the ENTIRE vertex list as one Catmull-Rom spline with the
            # first and last points acting as guides.  Fewer than 4 points draws
            # nothing at all.  Mixed vertex()/curveVertex() shapes in the
            # original art rely on exactly this.
            raw = [op[1] if op[0] != "b" else op[3] for op in t]
            if len(raw) > 3:
                pts.append(raw[1])
                for k in range(1, len(raw) - 2):
                    pts.extend(_catmull_points(raw[k - 1], raw[k], raw[k + 1],
                                               raw[k + 2], 14))
        else:
            for op in t:
                if op[0] == "b":
                    _, c1, c2, p3 = op
                    p0 = pts[-1] if pts else c1
                    pts.extend(_bezier_points(p0, c1, c2, p3,
                                              _segments_for(p0, p3, 60)))
                else:
                    pts.append(op[1])
        self._emit(pts, mode == CLOSE)

    # ----------------------------------------------------------- primitives --
    def ellipse(self, x, y, w, h):
        if self.ellipse_mode == CORNER:
            x, y = x + w / 2.0, y + h / 2.0
        rx, ry = w / 2.0, h / 2.0
        steps = int(constrain(max(abs(rx), abs(ry)) * self._mscale() * 0.9, 10, 64))
        pts = [self.pt(x + rx * cos(a * 360.0 / steps), y + ry * sin(a * 360.0 / steps))
               for a in range(steps)]
        self._emit(pts, True)

    def arc(self, x, y, w, h, start, stop):
        """Filled as a pie wedge (ProcessingJS behaviour); stroked as an open arc."""
        rx, ry = w / 2.0, h / 2.0
        span = abs(stop - start)
        steps = int(constrain(span / 6.0, 6, 64))
        arcpts = [self.pt(x + rx * cos(start + span * k / steps),
                          y + ry * sin(start + span * k / steps))
                  for k in range(steps + 1)]
        if self.do_fill:
            self._fill_poly([self.pt(x, y)] + arcpts)
        if self.do_stroke:
            self._stroke_path(arcpts, False)

    def _rect_pts(self, x, y, w, h, r=0):
        if self.rect_mode == CENTER:
            x, y = x - w / 2.0, y - h / 2.0
        r = constrain(abs(r), 0, min(abs(w), abs(h)) / 2.0)
        if r < 0.5:
            return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        pts = []
        steps = 6
        for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0),
                           (x + r, y + h - r, 90), (x + r, y + r, 180)):
            for k in range(steps + 1):
                a = a0 + 90.0 * k / steps
                pts.append((cx + r * cos(a), cy + r * sin(a)))
        return pts

    def rect(self, x, y, w, h, r=0):
        pts = [self.pt(px, py) for px, py in self._rect_pts(x, y, w, h, r)]
        self._emit(pts, True)

    def triangle(self, x1, y1, x2, y2, x3, y3):
        self._emit([self.pt(x1, y1), self.pt(x2, y2), self.pt(x3, y3)], True)

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self._emit([self.pt(x1, y1), self.pt(x2, y2),
                    self.pt(x3, y3), self.pt(x4, y4)], True)

    def line(self, x1, y1, x2, y2):
        if self.do_stroke:
            self._stroke_path([self.pt(x1, y1), self.pt(x2, y2)], False)

    def bezier(self, x1, y1, x2, y2, x3, y3, x4, y4):
        p0, p1 = self.pt(x1, y1), self.pt(x2, y2)
        p2, p3 = self.pt(x3, y3), self.pt(x4, y4)
        pts = [p0] + _bezier_points(p0, p1, p2, p3, _segments_for(p0, p3, 80))
        if self.do_fill:
            self._fill_poly(pts)
        if self.do_stroke:
            self._stroke_path(pts, False)


# -------------------------------------------------- module-level proxy API --
# Lets the transcribed art read like the ProcessingJS original.
_ctx: Gfx | None = None


def use(ctx: Gfx):
    global _ctx
    _ctx = ctx


def pushMatrix():  _ctx.push_matrix()
def popMatrix():   _ctx.pop_matrix()
def pushStyle():   _ctx.push_style()
def popStyle():    _ctx.pop_style()
def translate(x, y): _ctx.translate(x, y)
def scale(sx, sy=None): _ctx.scale(sx, sy)
def rotate(d):     _ctx.rotate(d)
def fill(*a):      _ctx.fill(*a)
def noFill():      _ctx.no_fill()
def stroke(*a):    _ctx.stroke(*a)
def noStroke():    _ctx.no_stroke()
def strokeWeight(w): _ctx.stroke_weight(w)
def rectMode(m):   _ctx.set_rect_mode(m)
def ellipseMode(m): _ctx.set_ellipse_mode(m)
def background(*a): _ctx.background(*a)
def beginShape():  _ctx.begin_shape()
def vertex(x, y):  _ctx.vertex(x, y)
def bezierVertex(a, b, c, d, e, f): _ctx.bezier_vertex(a, b, c, d, e, f)
def curveVertex(x, y): _ctx.curve_vertex(x, y)
def endShape(m=None): _ctx.end_shape(m)
def ellipse(x, y, w, h): _ctx.ellipse(x, y, w, h)
def arc(x, y, w, h, s, e): _ctx.arc(x, y, w, h, s, e)
def rect(x, y, w, h, r=0): _ctx.rect(x, y, w, h, r)
def triangle(*a):  _ctx.triangle(*a)
def quad(*a):      _ctx.quad(*a)
def line(*a):      _ctx.line(*a)
def bezier(*a):    _ctx.bezier(*a)


def blur(surface: pygame.Surface, radius: int = 1) -> pygame.Surface:
    """Cheap stand-in for Processing's filter(BLUR, r): downsample + upsample."""
    w, h = surface.get_size()
    f = max(2, int(radius) * 2)
    small = pygame.transform.smoothscale(surface, (max(1, w // f), max(1, h // f)))
    return pygame.transform.smoothscale(small, (w, h))


# ------------------------------------------------------- sprite blit cache --
_scale_cache: dict = {}
_rot_cache: dict = {}
_CACHE_MAX = 1400


def scaled(src: pygame.Surface, w: int, h: int) -> pygame.Surface:
    w, h = max(1, int(w)), max(1, int(h))
    if (w, h) == src.get_size():
        return src
    key = (id(src), w, h)
    got = _scale_cache.get(key)
    if got is None:
        if len(_scale_cache) > _CACHE_MAX:
            _scale_cache.clear()
        got = pygame.transform.smoothscale(src, (w, h))
        _scale_cache[key] = got
    return got


def image(dst, src, x, y, w=None, h=None):
    """Processing image() with the default CORNER imageMode."""
    if w is None:
        dst.blit(src, (int(round(x)), int(round(y))))
    else:
        dst.blit(scaled(src, w, h), (int(round(x)), int(round(y))))


def image_centered(dst, src, cx, cy, scl=1.0, angle=0.0):
    """translate(cx,cy); scale(s); rotate(a); image(src,-w/2,-h/2) - cached.

    Processing rotates clockwise (screen-space y is down); pygame rotates
    counter-clockwise, hence the negated angle.
    """
    sw, sh = src.get_size()
    tw, th = max(1, int(round(sw * scl))), max(1, int(round(sh * scl)))
    s = scaled(src, tw, th)
    a = round(angle, 1) % 360.0
    if a:
        key = (id(s), a)
        rot = _rot_cache.get(key)
        if rot is None:
            if len(_rot_cache) > _CACHE_MAX:
                _rot_cache.clear()
            rot = pygame.transform.rotate(s, -a)
            _rot_cache[key] = rot
        s = rot
    r = s.get_rect(center=(int(round(cx)), int(round(cy))))
    dst.blit(s, r)
