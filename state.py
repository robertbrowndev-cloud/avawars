"""state.py - the globals the original kept at ProcessingJS top level."""
from __future__ import annotations

WIDTH = 600
HEIGHT = 600

scene = "Load"

# input ---------------------------------------------------------------------
clicked = False          # true for exactly one frame, like Processing's mouseClicked
mouse_button = "LEFT"
mouse_x = 0
mouse_y = 0
want_hand = False        # set by anything that called cursor(HAND) this frame

frame_count = 0


class Keys:
    """Mimics ProcessingJS' `keys[keyCode]` and `keys[key]` dual indexing."""

    def __init__(self):
        self.codes: set[int] = set()
        self.chars: set[str] = set()

    def code(self, c: int) -> bool:
        return c in self.codes

    def char(self, ch: str) -> bool:
        return ch in self.chars

    def clear(self):
        self.codes.clear()
        self.chars.clear()


keys = Keys()

# entity lists --------------------------------------------------------------
pt = []    # particles
tr = []    # scene transitions
en = []    # enemies
gl = []    # glowing bullets
tl = []    # tiles
sel = []   # selection bar buttons

MAX_PARTICLES = 900   # soft cap the original lacked; keeps late waves smooth


def go(new_scene: str):
    global scene
    scene = new_scene
