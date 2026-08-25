"""
assets.py - bake every vector drawing routine into a Surface, exactly once.

This replaces the original's `img` object trick.  In ProcessingJS the game drew
each asset onto the *visible canvas* and grabbed it with `get(x, y, w, h)`,
which is why there is a full-screen "LOADING / Please be patient" scene with a
`background(0,0)` hack to hide the drawing in progress.

Here we render onto off-screen SRCALPHA surfaces instead:
  * nothing flashes on screen, so no hiding hack is needed;
  * assets are not limited to the canvas rectangle;
  * we can supersample and downscale for free antialiasing.

Assets are still produced one-per-frame so the loading screen stays responsive
(and so the pygbag/WebAssembly build never blocks the browser's main thread).
"""
from __future__ import annotations

import random

import pygame

import art
import pshim
from pshim import Gfx

# name -> (draw fn, width, height, supersample)
#
# Order matters: the loading bar advances through this list exactly like the
# original walked Object.keys(img).
SPECS = [
    ("hearts",             art.draw_hearts,             100, 100, 3),
    ("backdropfull",       art.draw_backdropfull,       600, 600, 1),
    ("backdrop2full",      art.draw_backdrop2full,      600, 600, 1),
    ("backdrop3full",      art.draw_backdrop3full,      600, 600, 1),
    ("backdrop1",          None,                        300, 600, 1),  # crop
    ("backdrop2",          art.draw_backdrop2,          600, 600, 1),
    ("backdrop3",          art.draw_backdrop3,          600, 600, 1),
    ("emerald",            art.draw_emerald,             65,  85, 3),
    ("money",              art.draw_money,              130, 130, 3),
    ("deletes",            art.draw_deletes,             60,  60, 3),
    ("snowBullet",         art.draw_snowBullet,         160, 160, 2),
    ("snowBulletUltimate", art.draw_snowBulletUltimate, 160, 160, 2),
    ("smolsnowBullet",     art.draw_smolsnowBullet,     160, 160, 2),
    ("iceBullet",          art.draw_iceBullet,          160, 160, 2),
    ("enemyBlt",           art.draw_enemyBlt,           160, 160, 2),
    ("FrostySaplings",     lambda: art.Frostsapling(205, 185, 3),   400, 400, 2),
    ("FrostySeed",         lambda: art.Frostseed(175, 185, 4),      400, 400, 2),
    ("FrostySeedling",     lambda: art.Frostseedling(205, 185, 3),  400, 400, 2),
    ("FrostyTree",         lambda: art.Frosttree(205, 200, 2.8),    400, 400, 2),
    ("FrostyUltimate",     lambda: art.Frostultimate(205, 200, 2.8), 400, 400, 2),
    ("VortanSeed",         lambda: art.Vortanseed(70, 60, 2.8),     400, 400, 2),
    ("VortanSeedling",     lambda: art.Vortanseedling(100, 0, 2),   400, 400, 2),
    ("VortanSapling",      lambda: art.Vortansapling(35, -40, 2.5), 400, 400, 2),
    ("VortanTree",         lambda: art.Vortantree(0, 100, 1),       400, 400, 2),
    ("VortanUltimate",     lambda: art.Vortanultimate(0, 100, 1),   400, 400, 2),
    ("frozen",             art.draw_frozen,             180, 180, 2),
]

TOTAL = len(SPECS)

img: dict[str, pygame.Surface] = {}


def _render(fn, w, h, ss) -> pygame.Surface:
    surf = pygame.Surface((w * ss, h * ss), pygame.SRCALPHA)
    ctx = Gfx(surf, scale=ss)
    pshim.use(ctx)
    fn()
    if ss != 1:
        surf = pygame.transform.smoothscale(surf, (w, h))
    return surf


def bake_one(index: int) -> str:
    """Bake asset `index`.  Returns its name."""
    name, fn, w, h, ss = SPECS[index]

    if name == "backdrop1":
        # identical geometry to backdropfull; the original re-rendered the whole
        # scene just to call get(300, 0, 300, 600).  A crop is exact and free.
        img[name] = img["backdropfull"].subsurface(pygame.Rect(300, 0, 300, 600)).copy()
        return name

    # the original's noise fields were baked once, so their randomness is part
    # of the art.  Seeding keeps every run identical, which the original was not.
    random.seed(1337 + index)
    surf = _render(fn, w, h, ss)

    if name == "backdrop2":
        surf = surf.subsurface(pygame.Rect(300, 0, 300, 600)).copy()
    elif name == "backdrop3":
        surf = pshim.blur(surf, 1)

    img[name] = surf
    return name
