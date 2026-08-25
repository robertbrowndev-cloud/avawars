"""scenes.py - the scene functions and the Manage_scenes dispatcher."""
from __future__ import annotations

import pygame

import assets
import entities as E
import pshim
import state
import ui
from assets import img
from pshim import CENTER, CORNER, color
from ui import Button, ShopBtn, Trans, gtext

W, H = state.WIDTH, state.HEIGHT

# --------------------------------------------------------------- buttons ----
go_back = Button(W / 2, H - 40, 200, 50, "Menu", "Return", color(230, 103, 18))
backs = Button(W / 2, 25, 200, 35, "Menu", "Return", color(61, 135, 255))
shop_back = Button(W / 2, H - 30, 200, 35, "Menu", "Return", color(33, 204, 44))
start_btn = Button(W - 140, H - 40, 200, 50, "Game", "New Battle", color(222, 22, 22))
shop_btn = Button(W / 4, H / 2, 180, 50, "Shop", "Shop", color(214, 21, 21))
how_btn = Button(W / 4, H / 1.4, 180, 50, "How", "How", color(214, 21, 21))
avatars_btn = Button(W / 4, H - 40, 180, 50, "About", "Avatars", color(214, 21, 21))

ggain = None
gamnt = None


def init_shop_buttons():
    global ggain, gamnt
    ggain = ShopBtn(W / 2, H - H / 4, 200, 35, "ggain", img["emerald"])
    gamnt = ShopBtn(W / 2, H / 3, 200, 35, "gamnt", img["emerald"])


# ================================================================== loading ==
class Load:
    def __init__(self):
        self.cur_load = 0
        self.loaded = False
        self.end_timer = 0.0
        self.end_it = False

    def draw(self, dst):
        total = assets.TOTAL
        if not self.loaded:
            assets.bake_one(self.cur_load)
            self.cur_load += 1

        if self.cur_load < total:
            self.loaded = False
        else:
            if not self.loaded:
                init_shop_buttons()
                E.build_world()
            self.loaded = True
            self.end_timer += 0.03

        if self.end_timer > 2 and not self.end_it:
            state.tr.append(Trans("Menu"))
            self.end_it = True

        dst.fill((103, 196, 85))
        gtext(dst, "L O A D I N G", W / 2, H / 4, W / 6, 5, color(34, 191, 45, 30))
        gtext(dst, "Please be patient", W / 2, H - H / 7, 56, 4, color(42, 214, 26, 30))

        bw = W / 1.5 + W / 50
        bar = pygame.Surface((int(bw), 25), pygame.SRCALPHA)
        bar.fill((28, 196, 19, 60))
        dst.blit(bar, (int(W / 2 - bw / 2), int(H / 2 + H / 10 - 12)))
        fw = (self.cur_load / total) * W / 1.5
        if fw >= 1:
            pygame.draw.rect(dst, (67, 186, 48),
                             (int(W / 2 - fw / 2), int(H / 2 + H / 10 - 7), int(fw), 15))


loader = Load()


# ===================================================================== game ==
def game(dst):
    dst.blit(img["backdrop3"], (0, 0))

    for t in state.tl:
        t.display(dst, E.admin)

    for e in list(state.en):
        e.draw(dst, E.admin)
    state.en[:] = [e for e in state.en if not e.die]

    for p in list(state.pt):
        p.draw(dst)
    state.pt[:] = [p for p in state.pt if not p.die]

    for b in list(state.gl):
        b.draw(dst)
    state.gl[:] = [b for b in state.gl if not b.die]

    E.spawn_enemies(E.admin)
    E.admin.draw(dst)

    if E.admin.health < 0 and len(state.tr) <= 0:
        E.admin.health = 0
        state.tr.append(Trans("Dead"))

    if E.admin.end_time <= 0 and len(state.tr) <= 0:
        state.tr.append(Trans("Win"))


# ============================================================ win / lose =====
def dead(dst):
    dst.blit(img["backdrop2full"], (0, 0))
    gtext(dst, "Battle Lost", W / 2, H / 4, W / 6, 5, color(235, 94, 0, 30))
    gtext(dst, "You lost the battle and\nhad to retreat. But this is\nnot the only battle",
          W / 2, H / 1.5, W / 15, 5, color(235, 94, 0, 30))
    go_back.draw(dst)


def win(dst):
    dst.blit(img["backdropfull"], (0, 0))
    gtext(dst, "Battle Won", W / 2, H / 4, W / 6, 5, color(235, 94, 0, 30))
    gtext(dst, "You won the battle and\nthe enemies retreated.\nBut be warned, they will never\ngive up fighting.",
          W / 2, H / 1.5, W / 15, 5, color(235, 94, 0, 30))
    go_back.draw(dst)


# ===================================================================== menu ==
def menu(dst):
    dst.blit(img["backdropfull"], (0, 0))
    gtext(dst, "AVAWARS", W / 2, H / 4.5, W / 4.5, 5, color(222, 0, 0, 30))
    E.Frostine(dst, 470, 370, 0.7, 0, 5)
    start_btn.draw(dst)
    shop_btn.draw(dst)
    how_btn.draw(dst)
    avatars_btn.draw(dst)
    E.admin.restart_battle()


# ============================================================= instructions ==
INSTRUCTIONS = (
    "Use the bar at the bottom of the screen to\n"
    "buy avatars. Defend your base against the\n"
    " Vortans! \n"
    " Defeat Vortan soldiers to gain gold.\n"
    "There is a small percentage chance that you\n"
    "can earn emeralds. Spend emeralds in the\n"
    "shop for better outcomes in a battle.\n"
    "\n"
    "To Select, just click your LEFT mouse button\n"
    "To sell an avatar, simply select it and press\n"
    "SPACE to do so. To de-select anything,\n"
    "just RIGHT click your mouse"
)


def instruct(dst):
    dst.blit(img["backdrop3"], (0, 0))
    gtext(dst, INSTRUCTIONS, W / 2, H / 2, 28, 5, color(222, 78, 0, 30))
    E.admin.display_stats(dst)
    go_back.draw(dst)


# ============================================================== avatar book ==
BOOK_TEXT = {
    1: "The Frostine Seed is a large, unhostile\ncreature. Though it may seem friendly,\n"
       "this creature is born with an extremely\nhard shell to protect it from preditors.\n\n"
       "Press SPACE to continue",
    2: "The Frostine Seedling is a small, creature.\nthough it cant do any damage,\n"
       "this creature can fire snowballs that \nfreeze their opponents.\n\n"
       "Press SPACE to continue",
    3: "This frostine Sapling is a strong creature\nthas just developed enough to shoot\n"
       "deadly snowballs.\n\nPress SPACE to continue",
    4: "Once the Sapling has grown to the tree stage,\nIt duplicates into 2 powerful creatures\n"
       "which are a more deadly\ncombo.\n\nPress SPACE to continue",
    5: "The final stage of the Frostine, is\nits Ultimate form. Its developed enough \n"
       "to be an extremely\npowerful asset on the battle field\n\nPress SPACE to continue",
}


class AvaBook:
    def __init__(self, kind):
        self.x = 0.0
        self.y = 0.0
        self.type = kind
        self.move_spd = 0.0
        self.move = False

    def draw(self, dst):
        E.Frostine(dst, W / 2 + self.x, H / 3 + self.y, 0.8, 0, self.type)
        if self.type == 2:
            # the original re-added this.x/this.y on top of the translate;
            # the double offset is part of the slide animation's look.
            E.Frostine(dst, W / 4 + 2 * self.x, H / 3 + 2 * self.y, 0.8, 0, self.type)
            E.Frostine(dst, W - W / 4 + 2 * self.x, H / 3 + 2 * self.y, 0.8, 0, self.type)
        gtext(dst, BOOK_TEXT[self.type], W / 2 + self.x, H / 1.5 + self.y,
              28, 5, color(0, 34, 255, 30))

        if state.keys.code(pygame.K_SPACE) and not self.move and self.move_spd <= 0.1:
            self.move = True
            self.move_spd = 70.0

        self.move_spd *= 0.9
        if self.move:
            self.y += self.move_spd

        if self.y > 600 and self.move_spd <= 0.1:
            self.move = False
            self.y = 0.0
            self.x = 600.0
            self.move_spd = 60.0
            self.type = self.type + 1 if self.type < 5 else 1

        if not self.move and self.x > 0:
            self.x -= self.move_spd
        else:
            if not self.move:
                self.x = 0.0


abook = AvaBook(1)


def about_us(dst):
    dst.blit(img["backdropfull"], (0, 0))
    abook.draw(dst)
    backs.draw(dst)


# ===================================================================== shop ==
def shops(dst):
    dst.blit(img["backdrop3full"], (0, 0))
    gtext(dst, "Starting Gold Amount", W / 2, H / 6, 28, 5, color(15, 179, 0, 30))
    gtext(dst, "Money Dropped By Enemys", W / 2, H / 2, 28, 5, color(15, 179, 0, 30))
    gtext(dst, f"{E.admin.gems} Gems", 50, H / 21, 28, 5, color(15, 179, 0, 30), CORNER)
    pshim.image(dst, img["emerald"], 0, 0, 40, 60)
    ggain.draw(dst, E.admin)
    gamnt.draw(dst, E.admin)
    shop_back.draw(dst)


# =================================================================== poster ==
def poster(dst):
    dst.fill((237, 218, 218))
    dst.blit(img["backdrop1"], (0, 0))
    dst.blit(img["backdrop2"], (300, 0))
    E.Frostine(dst, 126, 380, 0.6, 0, 5)
    E.Vortan(dst, 475, 346, 0.9, 0, 5)
    gtext(dst, "AVAWARS", W / 2, 100, 140, 0, color(219, 20, 20, 20))
    gtext(dst, "Corin Fist Productions", W / 2, 560, 50, 0, color(219, 20, 20, 20))


# ================================================================ dispatch ===
_SCENES = {
    "Game": game,
    "Dead": dead,
    "Menu": menu,
    "Win": win,
    "How": instruct,
    "About": about_us,
    "Shop": shops,
}


def manage_scenes(dst):
    if state.scene == "Load":
        loader.draw(dst)
    else:
        fn = _SCENES.get(state.scene)
        if fn:
            fn(dst)

    if state.keys.char("p") and loader.loaded:
        poster(dst)

    for t in list(state.tr):
        t.display(dst)
        t.update()
    state.tr[:] = [t for t in state.tr if not t.die]
