"""
entities.py - particles, bullets, enemies, defence tiles, the shop bar and the
Admin controller, ported 1:1 from the ProcessingJS original.

Deliberate deviations from the source are marked `# CHANGED:`.
"""
from __future__ import annotations

import math

import pygame

import pshim
import state
import ui
from assets import img
from pshim import constrain, dist, rnd, p_round, color

FROST = {1: "FrostySeed", 2: "FrostySeedling", 3: "FrostySaplings",
         4: "FrostyTree", 5: "FrostyUltimate"}
VORT = {1: "VortanSeed", 2: "VortanSeedling", 3: "VortanSapling",
        4: "VortanTree", 5: "VortanUltimate"}


def Frostine(dst, x, y, s, r, kind):
    pshim.image_centered(dst, img[FROST[kind]], x, y, s, r)


def Vortan(dst, x, y, s, r, kind):
    pshim.image_centered(dst, img[VORT[kind]], x, y, s, r)


def ptorect(x1, y1, x2, y2, w2, h2):
    return x2 < x1 < x2 + w2 and y2 < y1 < y2 + h2


def ctorect(cx, cy, cr, rx, ry, rw, rh):
    tsx = constrain(cx, rx, rx + rw)
    tsy = constrain(cy, ry, ry + rh)
    return math.hypot(cx - tsx, cy - tsy) <= cr / 2


# =============================================================== particles ===
class Partic:
    __slots__ = ("x", "y", "s", "texture", "type", "speed", "speed2",
                 "fade_time", "fade", "pause_time", "setup", "die")

    def __init__(self, x, y, s, texture, kind):
        self.x, self.y, self.s = x, y, s
        self.texture = texture
        self.type = kind
        self.speed = 0.0
        self.speed2 = 0.0
        self.fade_time = 0.0
        self.fade = 155.0
        self.pause_time = 0.0
        self.setup = False
        self.die = False

    def update(self):
        if not self.setup:
            t = self.type
            if t == 1:
                self.speed = rnd(1, 4)
                self.fade_time = rnd(3, 6)
                self.pause_time = 0.5
            elif t == 2:
                self.speed = rnd(1, 4)
                self.speed2 = rnd(-4, 4)
                self.fade_time = rnd(3, 6)
                self.pause_time = 0.5
            elif t == 3:
                self.fade_time = rnd(3, 6)
                self.pause_time = -3
            elif t == 4:
                self.speed = rnd(-2, 2)
                self.speed2 = rnd(-2, 2)
                self.fade_time = rnd(5, 8)
                self.pause_time = -2
            self.setup = True

        self.pause_time -= 0.025
        if self.pause_time <= 0:
            self.x += self.speed2
            self.y -= self.speed
            self.fade -= self.fade_time
            self.s -= self.fade_time / 13.0
        else:
            self.y += self.pause_time * 2
        if self.fade <= 0:
            self.die = True

    def draw(self, dst):
        ui.disc(dst, self.x, self.y, self.s, self.texture, self.fade)
        self.update()


# ================================================================= bullets ===
_BULLET_ART = {
    1: ("snowBullet", (97, 181, 255)),
    2: ("smolsnowBullet", (4, 117, 209)),
    3: ("snowBulletUltimate", (0, 49, 92)),
    4: ("iceBullet", (255, 255, 255)),
    5: ("enemyBlt", (255, 113, 5)),
}


class Glowers:
    __slots__ = ("x", "y", "s", "r", "dmg", "spd", "owner", "types",
                 "texture", "off_y", "timer", "die")

    def __init__(self, x, y, s, dmg, spd, owner, types):
        self.x, self.y, self.s = x, y, s
        self.r = rnd(0, 360)
        self.dmg = dmg
        self.spd = spd
        self.owner = owner
        self.types = types
        self.texture = (255, 255, 255)
        self.off_y = 50.0
        self.timer = 0.5
        self.die = False

    def update(self):
        self.off_y *= 0.7
        if self.off_y <= 0.1:
            self.timer -= 0.025
        if self.timer <= 0:
            self.r += self.spd
            if self.owner == "good":
                self.x += self.spd
                if self.x > state.WIDTH + 50:
                    self.die = True
            else:
                self.x -= self.spd
                if self.x < -50:
                    self.die = True
            if state.frame_count % 3 == 0 and len(state.pt) < state.MAX_PARTICLES:
                state.pt.append(Partic(self.x, self.y, self.s / 2, self.texture, 3))
        if self.die:
            for _ in range(20):
                if len(state.pt) >= state.MAX_PARTICLES:
                    break
                state.pt.append(Partic(self.x + rnd(-self.s / 2, self.s / 2),
                                       self.y + rnd(-self.s / 2, self.s / 2),
                                       self.s / 3, self.texture, 4))

    def draw(self, dst):
        name, tex = _BULLET_ART[self.types]
        self.texture = tex
        src = img[name]
        scl = (self.s * 2.0 / src.get_width()) * (1 + self.off_y / 20.0)
        pshim.image_centered(dst, src, self.x, self.y - self.off_y, scl, self.r)
        self.update()


# ================================================================= enemies ===
_ROW_Y = {1: 140, 2: 220, 3: 300, 4: 380, 5: 460}


class Enemies:
    def __init__(self, x, y, creature, row):
        self.x, self.y = x, y
        self.hitbox = 50
        self.creature = int(constrain(creature, 1, 5))
        self.row = int(constrain(row, 1, 5))
        self.setup = False
        self.health = 10.0
        self.dmg = 0.0
        self.bsze = 0
        self.spd = 0.0
        self.attack_time = 0.0
        self.attack_reld = 0.0
        self.frozen_time = 0.0
        self.gold = 0
        self.emerald = 0
        self.attacking = True
        self.die = False

    def setups(self, admin):
        c = self.creature
        hurry = admin.timer > 5
        if c == 1:
            self.health = rnd(20, 100)
            self.dmg = rnd()          # NOTE: original wrote `random()` -> 0..1 dmg
            self.spd = 0.5
            self.bsze = 30
            self.attack_time = 2
            self.gold = p_round(rnd(40, 90))
            self.emerald = p_round(rnd(10, 30))
        elif c == 2:
            self.health = rnd(50, 100) if hurry else rnd(150, 200)
            self.dmg = rnd(5, 10)
            self.spd = 1
            self.bsze = 30
            self.attack_time = 0.5
            self.gold = p_round(rnd(50, 120))
            self.emerald = p_round(rnd(20, 30))
        elif c == 3:
            self.health = rnd(150, 250) if hurry else rnd(200, 300)
            self.dmg = rnd(20, 30)
            self.spd = 4
            self.bsze = 30
            self.attack_time = 5
            self.gold = p_round(rnd(90, 150))
            self.emerald = p_round(rnd(30, 32))
        elif c == 4:
            self.health = rnd(200, 350) if hurry else rnd(350, 450)
            self.dmg = rnd(20, 40)
            self.spd = 4
            self.bsze = 20
            self.attack_time = 7
            self.gold = p_round(rnd(100, 190))
            self.emerald = p_round(rnd(30, 31))
        else:
            self.health = rnd(350, 450) if hurry else rnd(350, 640)
            self.dmg = rnd(30, 50)
            self.bsze = 25
            self.spd = 0.4
            self.attack_time = 5
            self.gold = p_round(rnd(200, 280))
            self.emerald = 30
        self.y = _ROW_Y[self.row]
        self.setup = True

    def looks(self, dst):
        c = self.creature
        if c == 1:
            Vortan(dst, self.x + 0, self.y + 0, 0.3, 0, 1)
        elif c == 2:
            Vortan(dst, self.x + 4, self.y - 31, 0.3, 0, 2)
        elif c == 3:
            Vortan(dst, self.x + 4, self.y - 9, 0.3, 0, 3)
        elif c == 4:
            Vortan(dst, self.x + 0, self.y - 9, 0.3, 0, 4)
        else:
            Vortan(dst, self.x + 0, self.y - 2, 0.4, 0, 5)

        if self.frozen_time > 0:
            # CHANGED: the ice cage is a pre-baked sprite instead of ~16 live
            # stroked vertices per frozen enemy per frame.
            pshim.image_centered(dst, img["frozen"], self.x, self.y, 1.0, 0)

    def update(self, admin):
        self.attacking = False
        self.frozen_time -= 0.023

        for t in state.tl:
            if t.type != "none":
                if t.x < self.x < t.x + 120 and t.y + 5 < self.y < t.y + 75:
                    self.attacking = True

        for b in state.gl:
            if b.owner == "good" and \
                    dist(b.x, b.y, self.x, self.y) < self.hitbox / 5 + b.s / 5:
                b.die = True
                self.health -= b.dmg
                if b.types == 4 and self.creature < 4:
                    self.frozen_time = rnd(3, 5)

        self.attack_reld -= 0.025

        if self.attacking and self.frozen_time <= 0:
            if self.attack_reld <= 0:
                self.attack_reld = self.attack_time
                state.gl.append(Glowers(self.x, self.y, self.bsze, self.dmg,
                                        10, "bad", 5))
        elif self.frozen_time <= 0:
            self.x -= self.spd

        if self.health <= 0:
            admin.money += self.gold * admin.money_gain
            if self.emerald == 30:
                admin.gems += 1
            self.die = True
            for _ in range(50):
                if len(state.pt) >= state.MAX_PARTICLES:
                    break
                state.pt.append(Partic(rnd(self.x - 30, self.x + 30),
                                       rnd(self.y - 25, self.y + 20),
                                       rnd(10, 20),
                                       (int(200 + rnd(55)), 117, 25), 2))

        if self.x < -30:
            self.die = True
            admin.health -= 5

    def draw(self, dst, admin):
        if not self.setup:
            self.setups(admin)
        if self.setup:
            self.update(admin)
        self.looks(dst)


def spawn_enemies(admin):
    admin.enemy_level = 6.0 / (admin.timer / 4.0)
    admin.choostme -= 0.025
    if admin.timer > 5:
        admin.timer -= 0.002
    if admin.choostme <= 0:
        admin.choostme = p_round(rnd(1, admin.timer))
        state.en.append(Enemies(rnd(720, 800), 0,
                                p_round(rnd(1, admin.enemy_level)),
                                p_round(rnd(1, 5))))


# ============================================================== selections ===
COSTS = {"freezer": 50, "regular": 100, "twin": 150, "barrier": 200, "cannon": 350}
TYPES = ["freezer", "regular", "twin", "barrier", "cannon"]


def draw_defender(dst, x, y, kind, bob=0.0):
    """The little Frostine cluster used for a defender of each type."""
    if kind == "freezer":
        Frostine(dst, x + 20, y + bob * 0.5, 0.1, 0, 2)
        Frostine(dst, x, y + bob, 0.1, 0, 2)
        Frostine(dst, x - 20, y + bob * 0.5, 0.1, 0, 2)
    elif kind == "regular":
        Frostine(dst, x, y - 3, 0.2, 0, 3)
    elif kind == "twin":
        Frostine(dst, x - 20, y - 3, 0.2, 0, 4)
        Frostine(dst, x + 20, y - 3, 0.2, 0, 4)
    elif kind == "barrier":
        Frostine(dst, x, y, 0.2, 0, 1)
    elif kind == "cannon":
        Frostine(dst, x, y - 6, 0.2, 0, 5)


class Selection:
    def __init__(self, x, y, kind):
        self.x, self.y = x, y
        self.hitbox = 80
        self.type = kind
        self.cost = COSTS[kind]     # CHANGED: known up-front, not on first draw
        self.hover = False

    def draw(self, dst, admin):
        if self.hover:
            col = (118, 173, 107, 30) if admin.money >= self.cost else (219, 28, 28, 50)
            box = pygame.Surface((self.hitbox, self.hitbox), pygame.SRCALPHA)
            box.fill(col)
            dst.blit(box, (int(self.x - self.hitbox / 2), int(self.y - self.hitbox / 2)))

        draw_defender(dst, self.x, self.y, self.type)

        if self.hover:
            tex = color(240, 204, 22, 30) if admin.money >= self.cost \
                else color(240, 24, 24, 30)
            ui.gtext(dst, self.cost, self.x, self.y + 10, 25, 4, tex)

        self.hover = ptorect(state.mouse_x, state.mouse_y,
                             self.x - self.hitbox / 2, self.y - self.hitbox / 2,
                             self.hitbox, self.hitbox)
        if self.hover:
            state.want_hand = True
            if state.clicked and admin.money >= self.cost:
                admin.in_hand = self.type
                admin.spend_money = self.cost


# =================================================================== tiles ===
_TILE_HEALTH = {"freezer": 50, "regular": 150, "twin": 200,
                "barrier": 400, "cannon": 350}


class Tiles:
    def __init__(self, x, y, s):
        self.x, self.y, self.s = x, y, s
        self.hovered = False
        self.fade_in = 60.0
        self.delete_it = False
        self.type = "none"
        self.cost = 0.0
        self.damage = 0.0
        self.reload_time = 0.0
        self.reload = rnd(0, 2)
        self.bullet_spd = 0.0
        self.health = 10.0
        self.die = False
        self.occupied = False

    def set_health(self):
        self.health = _TILE_HEALTH.get(self.type, 10)

    def select(self, admin):
        if ptorect(state.mouse_x, state.mouse_y, self.x, self.y, self.s, self.s):
            self.hovered = True
            self.fade_in *= 0.7
            state.want_hand = True
            if state.clicked and state.mouse_button == "LEFT":
                if self.type != "none":
                    self.delete_it = True
                elif admin.in_hand != "nothing" and not self.occupied:
                    self.type = admin.in_hand
                    self.set_health()
                    admin.in_hand = "nothing"
                    admin.money -= admin.spend_money
                    self.cost = admin.spend_money / 1.2
        else:
            if state.clicked:
                self.delete_it = False
            self.hovered = False
            self.fade_in += 4

        if self.delete_it and (state.keys.code(pygame.K_DELETE) or
                               state.keys.code(pygame.K_SPACE)):
            admin.money += self.cost
            self.die = True
            self.delete_it = False

        self.fade_in = constrain(self.fade_in, 0, 60)

    def update_avatars(self):
        self.reload -= 0.026
        self.occupied = False
        t = self.type

        if t == "freezer":
            self.damage, self.reload_time, self.bullet_spd = 0, 7, 10
            if self.reload <= 0:
                self.reload = self.reload_time
                for dx in (10, 40, 65):
                    state.gl.append(Glowers(self.x + dx, self.y + 45, 10,
                                            self.damage, self.bullet_spd, "good", 4))
        elif t == "regular":
            self.damage, self.reload_time, self.bullet_spd = 10, 2, 10
            if self.reload <= 0:
                self.reload = self.reload_time
                state.gl.append(Glowers(self.x + 40, self.y + 45, 30,
                                        self.damage, self.bullet_spd, "good", 1))
        elif t == "twin":
            self.damage, self.reload_time, self.bullet_spd = 7, 1.5, 13
            if self.reload <= 0:
                self.reload = self.reload_time
                for dx in (15, 55):
                    state.gl.append(Glowers(self.x + dx, self.y + 45, 30,
                                            self.damage, self.bullet_spd, "good", 2))
        elif t == "cannon":
            self.damage, self.reload_time, self.bullet_spd = 35, 2, 8
            if self.reload <= 0:
                self.reload = self.reload_time
                state.gl.append(Glowers(self.x + 40, self.y + 55, 40,
                                        self.damage, self.bullet_spd, "good", 3))
        # "barrier" and "none" simply never fire

        if t != "none":
            cx, cy = self.x + self.s / 2, self.y + self.s / 2
            for b in state.gl:
                if b.owner == "bad" and dist(b.x, b.y, cx, cy) < 10:
                    b.die = True
                    self.health -= b.dmg

        for e in state.en:
            if ctorect(e.x, e.y, e.hitbox, self.x, self.y, self.s, self.s):
                self.occupied = True

        if self.health <= 0:
            self.die = True

    def handle_death(self):
        if self.die:
            for _ in range(30):
                if len(state.pt) >= state.MAX_PARTICLES:
                    break
                state.pt.append(Partic(rnd(self.x + 10, self.x + self.s - 10),
                                       rnd(self.y + 10, self.y + self.s - 10),
                                       rnd(15, 20),
                                       (140, 209, int(200 + rnd(55))), 2))
            self.type = "none"
            self.die = False
            self.health = 100

    def display_items(self, dst):
        cx, cy = self.x + self.s / 2, self.y + self.s / 2
        f = state.frame_count
        t = self.type
        if t == "freezer":
            Frostine(dst, cx + 26, cy + math.sin(math.radians(f * 4)) * 2.6, 0.13, 0, 2)
            Frostine(dst, cx, cy + math.sin(math.radians(f * 4)) * 5.2, 0.13, 0, 2)
            Frostine(dst, cx - 26, cy + math.sin(math.radians(f * 4)) * 2.6, 0.13, 0, 2)
        elif t == "regular":
            Frostine(dst, cx + 6.5, cy - 20.8, 0.221,
                     -4 + math.cos(math.radians(f * 5)), 3)
        elif t == "twin":
            Frostine(dst, cx - 18.2, cy - 13, 0.208, 0, 4)
            Frostine(dst, cx + 22.1, cy - 13, 0.208, 0, 4)
        elif t == "barrier":
            Frostine(dst, cx + 3.9, cy + 2.6, 0.234, 0, 1)
        elif t == "cannon":
            Frostine(dst, cx + 5.2, cy - 2.6, 0.208, 0, 5)

    def display(self, dst, admin):
        ui.dim_rect(dst, self.x, self.y, self.s, self.s, 60 - self.fade_in)
        self.display_items(dst)
        if self.delete_it:
            ui.dim_rect(dst, self.x, self.y, self.s, self.s, self.fade_in)
        self.select(admin)
        self.update_avatars()
        self.handle_death()


# =================================================================== admin ===
class Admin:
    def __init__(self):
        self.start_amount = 400.0
        self.start_health = 100
        self.money_gain = 1.0

        self.money = self.start_amount
        self.gems = 10
        self.health = 100

        self.timer = 20.0
        self.choostme = 0.0
        self.enemy_level = 2.0
        self.end_time = 300.0

        self.in_hand = "nothing"
        self.spend_money = 0.0

        self.scroll_y = 0.0
        self.scroll_spd = 0.0

    def restart_battle(self):
        self.money = self.start_amount
        self.health = self.start_health
        self.timer = 20.0
        self.end_time = 300.0
        self.enemy_level = 2.0
        self.choostme = 0.0
        self.in_hand = "nothing"
        self.scroll_y = 0.0
        self.scroll_spd = 0.0
        self.spend_money = 0.0
        state.en.clear()
        state.gl.clear()
        for t in state.tl:
            t.type = "none"

    def in_hands(self, dst):
        if self.in_hand != "nothing":
            draw_defender(dst, state.mouse_x, state.mouse_y, self.in_hand)

    def display_selections(self, dst):
        for s in state.sel:
            s.draw(dst, self)
            s.y = 646 - self.scroll_y
        if state.clicked and state.mouse_button == "RIGHT":
            self.in_hand = "nothing"
            for t in state.tl:
                t.delete_it = False

    def update_bar(self):
        if state.mouse_y > 580 - self.scroll_y:
            self.scroll_y += self.scroll_spd
            self.scroll_spd *= 0.85
        else:
            self.scroll_y *= 0.8
            self.scroll_spd = 13.0
        self.scroll_y = constrain(self.scroll_y, 0, 90)
        self.money += 0.015
        self.end_time -= 0.023

    def display_stats(self, dst):
        w, h = state.WIDTH, state.HEIGHT
        band = ui.hud_strip("band")
        dst.blit(band, (0, int(588 - self.scroll_y)))
        dst.blit(band, (0, 30))

        pygame.draw.rect(dst, (240, 240, 240), (0, int(600 - self.scroll_y), w, 500))
        pygame.draw.rect(dst, (240, 240, 240), (0, 0, w, 40))
        pygame.draw.rect(dst, (240, 240, 240),
                         (int(w / 2 - w / 12), int(580 - self.scroll_y),
                          int(w / 6), 500), border_radius=10)

        handle = ui.hud_strip("handle")
        dst.blit(handle, (int(w / 2 - handle.get_width() / 2),
                          int(582 - self.scroll_y)))

        pshim.image(dst, img["emerald"], 14, 2, 25, 35)
        pshim.image(dst, img["money"], 220, 1, 70, 70)
        pshim.image(dst, img["hearts"], 423, -5, 50, 50)

        from pshim import CORNER
        ui.gtext(dst, self.gems, 60, 20, 36, 4, color(53, 186, 0, 30), CORNER)
        ui.gtext(dst, p_round(self.money), 270, 20, 36, 4, color(247, 215, 10, 30), CORNER)
        ui.gtext(dst, int(self.health), 479, 20, 36, 4, color(247, 121, 132, 30), CORNER)

    def draw(self, dst):
        self.display_stats(dst)
        self.update_bar()
        self.display_selections(dst)
        self.in_hands(dst)


admin = Admin()


def build_world():
    """Recreate the ProcessingJS top-level `for` loops that filled sel[] and tl[]."""
    state.sel.clear()
    for i, kind in enumerate(TYPES):
        state.sel.append(Selection(100 + i * 100, 550, kind))
    state.tl.clear()
    for x in range(6):
        for y in range(5):
            state.tl.append(Tiles(x * 80, 100 + y * 80, 80))
