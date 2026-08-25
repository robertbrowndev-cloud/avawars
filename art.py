"""
art.py - every drawing routine from the original AVAWARS program, transcribed.

These are pure vector-drawing functions.  They are called exactly once each,
during the loading screen, to bake a Surface (see assets.py).  Nothing in here
runs during gameplay.
"""
from pshim import (  # noqa: F401
    pushMatrix, popMatrix, pushStyle, popStyle, translate, scale, rotate,
    fill, noFill, stroke, noStroke, strokeWeight, rectMode, ellipseMode,
    background, beginShape, vertex, bezierVertex, curveVertex, endShape,
    ellipse, arc, rect, triangle, quad, line, bezier,
    CENTER, CORNER, CLOSE, color, rnd, sin, cos,
)

WIDTH = 600
HEIGHT = 600


# =========================================================== shared scenery ==
def trees(x=None, y=None, sx=None, sy=None):
    # NOTE: the original calls bare `trees()` twice inside the backdrops.  In JS
    # that made the CTM NaN and the whole thing silently vanished, so it is dead
    # code.  We reproduce the (non-)effect by bailing out.
    if x is None or y is None or sx is None or sy is None:
        return
    pushMatrix()
    pushStyle()
    translate(x, y)
    scale(sx, sy)

    noStroke()
    fill(237, 254, 255)
    beginShape()
    vertex(150, 350)
    bezierVertex(130, 347, 50, 313, 20, 290)
    bezierVertex(25, 260, 55, 274, 80, 292)
    bezierVertex(-10, 20, 140, -75, 173, 110)
    bezierVertex(265, 115, 220, 300, 180, 343)
    endShape()

    fill(177, 216, 250)
    beginShape()
    vertex(150, 350)
    bezierVertex(130, 347, 50, 313, 20, 290)
    bezierVertex(40, 280, 60, 283, 80, 292)
    bezierVertex(0, 50, 110, -75, 160, 130)
    bezierVertex(220, 130, 225, 230, 170, 345)
    endShape()

    fill(127, 131, 176)
    beginShape()
    vertex(150, 375)
    vertex(163, 375)
    vertex(157, 327)
    vertex(137, 240)
    vertex(150, 160)
    vertex(133, 230)
    vertex(95, 70)
    vertex(150, 330)
    vertex(100, 297)
    vertex(150, 340)
    endShape()

    popStyle()
    popMatrix()


# ========================================================= Frostine avatars ==
def Frostseed(x, y, s):
    pushMatrix()
    translate(x, y)
    scale(s)

    noStroke()
    fill(121, 148, 166)
    ellipse(4, 13, 69, 60)
    beginShape()
    vertex(0, -26)
    bezierVertex(0, -24, 29, -19, 36, 2)
    endShape()

    fill(195, 218, 235)
    beginShape()
    vertex(-28, 0)
    bezierVertex(-16, -19, -4, -23, 1, -35)
    bezierVertex(1, -19, 26, -15, 30, 0)
    bezierVertex(38, 27, 15, 38, 2, 38)
    bezierVertex(-19, 38, -39, 25, -28, 0)
    endShape()

    fill(0, 50)
    ellipse(-11, 24, 6, 6)
    ellipse(11, 21, 6, 6)

    fill(255)
    ellipse(11, 20, 3, 3)
    ellipse(-11, 23, 3, 3)
    popMatrix()


def _frost_body_shadow():
    fill(121, 148, 166)
    beginShape()
    vertex(34, -58)
    bezierVertex(24, -45, 25, -35, 24, -31)
    bezierVertex(29, -1, 15, -1, 5, 5)
    bezierVertex(-4, 9, -7, 8, -10, 14)
    vertex(-9, 17)
    bezierVertex(-1, 17, 13, 20, 15, 38)
    bezierVertex(14, 47, 14, 53, 1, 61)
    bezierVertex(-11, 63, -15, 62, -23, 54)
    vertex(-11, 20)
    vertex(-14, -5)
    vertex(14, -45)
    vertex(34, -58)
    endShape()


def _frost_body_shading(r, g, b):
    fill(r, g, b)
    beginShape()
    vertex(0, -25)
    bezierVertex(20, -45, 22, -35, 23, -33)
    bezierVertex(28, -1, 18, -3, 7, 4)
    bezierVertex(-5, 12, -7, 5, -5, -9)
    bezierVertex(-8, -25, -25, 5, 0, -25)
    endShape()


def _frost_body_main():
    fill(195, 218, 235)
    beginShape()
    vertex(-12, 15)
    bezierVertex(-31, -11, -4, -35, -3, -35)
    bezierVertex(11, -48, 12, -48, 34, -59)
    bezierVertex(21, -48, -8, -23, -10, 16)
    bezierVertex(-4, 20, -8, 17, 2, 23)
    bezierVertex(16, 37, 7, 54, -3, 58)
    bezierVertex(-14, 62, -20, 58, -25, 51)
    bezierVertex(-31, 39, -21, 25, -19, 23)
    bezierVertex(-11, 15, -13, 20, -12, 15)
    endShape()


def _frost_veins():
    noFill()
    strokeWeight(2)
    stroke(78, 97, 133)
    bezier(29, -54, -17, -28, -17, -10, -12, 16)
    bezier(25, -48, 2, -20, -8, -25, -7, 16)
    bezier(23, -38, 8, -20, 5, -25, -10, 16)
    bezier(23, -33, 27, -3, 5, -7, -9, 16)
    bezier(30, -54, 19, -41, 25, -36, 23.5, -30)
    noStroke()


def _frost_ears():
    fill(195, 216, 232)
    beginShape()
    vertex(-24, 31)
    bezierVertex(-32, -2, -11, 24, -11, 19)
    endShape()

    fill(175, 175, 209)
    beginShape()
    vertex(-21, 31)
    bezierVertex(-29, 7, -16, 22, -13, 23)
    endShape()

    pushMatrix()
    translate(-10, 0)
    scale(-1, 1)
    fill(195, 216, 232)
    beginShape()
    vertex(-24, 31)
    bezierVertex(-32, -2, -11, 24, -11, 19)
    endShape()

    fill(175, 175, 209)
    beginShape()
    vertex(-21, 31)
    bezierVertex(-29, 7, -16, 22, -13, 23)
    endShape()
    popMatrix()


def _frost_leaf():
    fill(121, 148, 166)
    beginShape()
    vertex(34, -58)
    bezierVertex(24, -45, 25, -35, 24, -31)
    bezierVertex(29, -1, 15, -1, 5, 5)
    bezierVertex(-4, 9, -7, 8, -6, 14)
    vertex(-14, 17)
    vertex(-5, 13)
    vertex(-14, -5)
    vertex(14, -45)
    vertex(34, -58)
    endShape()

    _frost_body_shading(130, 159, 176)

    fill(195, 218, 235)
    beginShape()
    vertex(-12, 15)
    bezierVertex(-31, -11, -4, -35, -3, -35)
    bezierVertex(11, -48, 12, -48, 34, -59)
    bezierVertex(21, -48, -8, -23, -10, 16)
    endShape()

    _frost_veins()


def Frostseedling(x, y, s):
    noStroke()
    pushMatrix()
    translate(x, y)
    scale(s)

    _frost_body_shadow()
    _frost_body_shading(130, 159, 176)
    _frost_body_main()

    pushMatrix()
    fill(195, 218, 235)
    rotate(66)
    ellipse(56, 18, 8, 15)
    fill(145, 179, 204)
    ellipse(58, 18, 6, 13)
    popMatrix()

    pushMatrix()
    fill(195, 218, 235)
    rotate(92)
    ellipse(66, 18, 8, 15)
    fill(145, 179, 204)
    ellipse(67, 18, 5, 12)
    popMatrix()

    fill(0, 50)
    ellipse(-18, 49, 5, 5)
    ellipse(-4, 46, 5, 5)

    fill(255)
    ellipse(-18, 48, 2, 2)
    ellipse(-4, 45, 2, 2)
    popMatrix()


def Frostsapling(x, y, s):
    noStroke()
    pushMatrix()
    translate(x, y)
    scale(s)

    _frost_ears()
    _frost_body_shadow()
    _frost_body_shading(143, 170, 186)
    _frost_body_main()
    _frost_veins()

    pushMatrix()
    translate(12, 3)
    rotate(80)
    fill(195, 218, 235)
    ellipse(56, 18, 8, 15)
    fill(145, 179, 204)
    ellipse(58, 18, 6, 13)
    popMatrix()

    pushMatrix()
    fill(195, 218, 235)
    rotate(92)
    ellipse(66, 18, 8, 15)
    fill(145, 179, 204)
    ellipse(67, 18, 5, 12)
    popMatrix()

    fill(0, 50)
    ellipse(-18, 47, 5, 5)
    ellipse(-4, 46, 5, 5)

    fill(255)
    ellipse(-19, 47, 2, 2)
    ellipse(-5, 46, 2, 2)
    popMatrix()


def Frosttree(x, y, s):
    noStroke()
    pushMatrix()
    translate(x, y)
    scale(s)

    _frost_ears()
    _frost_body_shadow()
    _frost_body_shading(143, 170, 186)
    _frost_body_main()
    _frost_veins()

    pushMatrix()
    translate(8, 7)
    rotate(19)
    _frost_leaf()
    popMatrix()

    pushMatrix()
    translate(-10, -2)
    rotate(-41)
    _frost_leaf()
    popMatrix()

    pushMatrix()
    translate(12, 3)
    rotate(80)
    fill(195, 218, 235)
    ellipse(56, 18, 8, 15)
    fill(145, 179, 204)
    ellipse(58, 18, 6, 13)
    popMatrix()

    pushMatrix()
    fill(195, 218, 235)
    rotate(92)
    ellipse(66, 18, 8, 15)
    fill(145, 179, 204)
    ellipse(67, 18, 5, 12)
    popMatrix()

    fill(0, 50)
    ellipse(-17, 47, 5, 5)
    ellipse(-4, 47, 5, 5)

    fill(255)
    ellipse(-16, 47, 2, 2)
    ellipse(-3, 47, 2, 2)
    popMatrix()


def Frostultimate(x, y, s):
    noStroke()
    pushMatrix()
    translate(x, y)
    scale(s)

    # wings
    fill(240, 240, 240)
    strokeWeight(0.5)
    stroke(145, 145, 145)
    beginShape()
    vertex(-15, 24)
    bezierVertex(-25, 9, -30, 26, -57, 6)
    bezierVertex(-59, 16, -30, 26, -41, 21)
    bezierVertex(-61, 18, -30, 36, -31, 36)
    bezierVertex(-54, 31, -30, 48, -22, 47)
    endShape()

    pushMatrix()
    translate(-10, 0)
    scale(-1, 1)
    beginShape()
    vertex(-15, 24)
    bezierVertex(-25, 9, -30, 26, -57, 6)
    bezierVertex(-59, 16, -30, 26, -41, 21)
    bezierVertex(-61, 18, -30, 36, -31, 36)
    bezierVertex(-54, 31, -30, 48, -22, 47)
    endShape()
    popMatrix()

    line(-41, 21, -19, 32)
    line(-31, 36, -19, 42)
    line(32, 21, -19, 39)
    line(21, 36, -19, 52)

    noStroke()

    _frost_ears()
    _frost_body_shadow()
    _frost_body_shading(143, 170, 186)
    _frost_body_main()
    _frost_veins()

    pushMatrix()
    translate(8, 7)
    rotate(19)
    _frost_leaf()
    popMatrix()

    pushMatrix()
    translate(-10, -2)
    rotate(-41)
    _frost_leaf()
    popMatrix()

    # unicorn horn
    fill(255, 255, 255)
    beginShape()
    vertex(-10, 20)
    bezierVertex(-6, 10, -5, 6, -2, 3)
    bezierVertex(2, 5, -5, 24, -2, 22)
    endShape()

    stroke(191, 110, 245)
    strokeWeight(2)
    line(-5, 10, -2, 10)
    line(-6, 13, -2, 14)
    line(-8, 16, -2, 18)
    line(-9, 19, -3, 21)

    noFill()
    strokeWeight(0.4)
    stroke(80)
    beginShape()
    vertex(-10, 20)
    bezierVertex(-6, 10, -5, 6, -2, 3)
    bezierVertex(2, 5, -5, 24, -2, 22)
    endShape(CLOSE)

    noStroke()

    pushMatrix()
    translate(12, 4)
    rotate(80)
    fill(195, 218, 235)
    ellipse(56, 18, 8, 15)
    fill(145, 179, 204)
    ellipse(58, 18, 6, 13)
    popMatrix()

    pushMatrix()
    fill(195, 218, 235)
    rotate(92)
    ellipse(63, 14, 8, 15)
    fill(145, 179, 204)
    ellipse(64, 14, 5, 12)
    popMatrix()

    fill(0, 50)
    ellipse(-18, 47, 5, 5)
    ellipse(-4, 47, 5, 5)

    fill(255)
    ellipse(-19, 46, 2, 2)
    ellipse(-5, 46, 2, 2)
    popMatrix()


# =========================================================== Vortan avatars ==
vc = [color(133, 29, 0), color(184, 31, 0), color(212, 74, 0), color(184, 37, 0),
      color(184, 64, 0), color(212, 92, 0), color(212, 85, 0)]


def Vortanseed(x, y, s):
    pushMatrix()
    translate(x, y)
    scale(s)
    noStroke()
    fill(vc[0])
    ellipse(48, 57, 75, 75)
    fill(vc[2])
    ellipse(45, 55, 71, 67)
    fill(vc[1])
    triangle(21, 30, 71, 27, 42, 8)
    fill(vc[2])
    triangle(21, 31, 67, 28, 42, 8)
    fill(51, 76, 125)
    arc(58, 68, 12, 12, -28, 154)
    arc(32, 68, 12, 12, 31, 207)
    fill(140, 140, 140)
    ellipse(57, 71, 3, 3)
    ellipse(33, 71, 3, 3)
    popMatrix()


def Vortanseedling(x, y, s):
    noStroke()
    pushMatrix()
    translate(x, y)
    scale(s)
    fill(vc[0])
    beginShape()
    vertex(203, 79)
    vertex(98, 8)
    curveVertex(85, 79)
    vertex(36, 117)
    endShape(CLOSE)
    triangle(99, 8, 32, 126, 40, 65)
    ellipse(46, 149, 65, 65)

    fill(vc[1])
    beginShape()
    vertex(48, 136)
    vertex(101, 9)
    curveVertex(39, 50)
    curveVertex(26, 100)
    vertex(36, 121)
    curveVertex(50, 76)
    vertex(101, 9)
    endShape(CLOSE)
    ellipse(43, 146, 60, 60)

    fill(0, 67, 125)
    arc(52, 158, 12, 12, -28, 154)
    arc(29, 158, 12, 12, 31, 207)
    fill(140, 140, 140)
    ellipse(30, 161, 3, 3)
    ellipse(51, 161, 3, 3)

    fill(vc[4])
    beginShape()
    curveVertex(-69, 199)
    curveVertex(62, 188)
    curveVertex(74, 170)
    curveVertex(55, 187)
    curveVertex(103, 279)
    endShape()
    ellipse(24, 184, 24, 12)

    fill(vc[3])
    ellipse(24, 186, 24, 10)
    beginShape()
    curveVertex(-42, 199)
    curveVertex(62, 187)
    curveVertex(74, 175)
    curveVertex(59, 178)
    curveVertex(56, 187)
    curveVertex(103, 279)
    endShape()
    popMatrix()


def Vortansapling(x, y, s):
    pushMatrix()
    translate(x, y)
    scale(s)
    noStroke()
    fill(vc[0])
    beginShape()
    vertex(130, 120)
    bezierVertex(71, 74, 157, 164, 37, 159)
    bezierVertex(130, 146, -98, 65, 97, 89)
    endShape()
    fill(vc[1])
    beginShape()
    vertex(121, 113)
    bezierVertex(63, 70, 155, 155, 44, 159)
    bezierVertex(137, 144, -88, 65, 97, 91)
    endShape()
    translate(-8, -188)
    fill(vc[4])
    ellipse(68, 257, 75, 75)
    fill(vc[2])
    ellipse(65, 256, 70, 70)
    triangle(38, 276, 99, 269, 68, 305)

    fill(0, 67, 125)
    arc(78, 268, 12, 12, -28, 154)
    arc(52, 268, 12, 12, 31, 207)
    fill(140, 140, 140)
    ellipse(77, 271, 3, 3)
    ellipse(53, 271, 3, 3)
    popMatrix()


def Vortantree(x, y, s):
    pushMatrix()
    translate(x, y)
    scale(s)
    noStroke()
    fill(vc[0])
    beginShape()
    vertex(270, 120)
    bezierVertex(154, 119, 248, 204, 175, 233)
    bezierVertex(254, 146, 42, 67, 233, 89)
    endShape()
    fill(vc[1])
    beginShape()
    vertex(270, 120)
    bezierVertex(210, 65, 245, 198, 175, 233)
    bezierVertex(260, 146, 42, 67, 233, 89)
    endShape()
    translate(130, -189)
    fill(vc[4])
    ellipse(68, 257, 75, 75)
    fill(vc[2])
    ellipse(65, 256, 70, 70)
    triangle(38, 276, 99, 269, 68, 305)
    fill(0, 67, 125)
    arc(78, 268, 12, 12, -28, 154)
    arc(52, 268, 12, 12, 31, 207)
    fill(138, 138, 138)
    ellipse(77, 271, 3, 3)
    ellipse(53, 271, 3, 3)
    fill(vc[3])
    beginShape()
    vertex(113, 287)
    bezierVertex(134, 194, 224, 249, 253, 268)
    bezierVertex(189, 194, 94, 150, 99, 281)
    endShape()
    beginShape()
    translate(-77, -2)          # yes, mid-shape: PJS applies the CTM at endShape
    vertex(116, 282)
    bezierVertex(76, 134, -11, 250, -37, 271)
    bezierVertex(101, 201, 65, 289, 124, 302)
    endShape()
    popMatrix()


def Vortanultimate(x, y, s):
    pushMatrix()
    translate(x, y)
    scale(s)

    pushMatrix()
    translate(-70, -13)
    fill(vc[0])
    noStroke()
    triangle(233, 65, 250, 62, 234, 25)
    triangle(299, 67, 280, 62, 287, 25)
    noFill()
    stroke(184, 0, 0)
    strokeWeight(3)
    arc(261, 26, 57, 9, -194, 12)
    noStroke()
    fill(vc[1])
    triangle(236, 65, 246, 62, 236, 36)
    triangle(295, 67, 284, 62, 287, 34)
    popMatrix()

    noStroke()
    translate(140, 0)
    fill(vc[2])
    beginShape()
    vertex(130, 120)
    bezierVertex(84, 79, 108, 204, 35, 233)
    bezierVertex(114, 146, -98, 67, 93, 89)
    endShape()

    fill(vc[3])
    beginShape()
    vertex(130, 120)
    bezierVertex(72, 65, 105, 198, 35, 233)
    bezierVertex(130, 146, -98, 67, 93, 89)
    endShape()
    translate(-10, -189)
    fill(vc[4])
    ellipse(68, 257, 75, 75)

    fill(vc[5])
    ellipse(65, 256, 70, 70)
    triangle(38, 276, 99, 269, 68, 305)
    fill(0, 67, 125)
    arc(78, 268, 12, 12, -28, 154)
    arc(52, 268, 12, 12, 31, 207)
    fill(138, 138, 138)
    ellipse(77, 271, 3, 3)
    ellipse(53, 271, 3, 3)
    fill(vc[3])
    beginShape()
    vertex(113, 287)
    bezierVertex(134, 194, 224, 249, 253, 268)
    bezierVertex(189, 194, 94, 150, 99, 281)
    endShape()
    beginShape()
    translate(-75, 0)
    vertex(116, 282)
    bezierVertex(76, 134, -11, 250, -37, 271)
    bezierVertex(101, 201, 65, 289, 124, 302)
    endShape()
    fill(vc[6])
    translate(76, -1)
    beginShape()
    vertex(109, 286)
    bezierVertex(125, 181, 230, 245, 248, 268)
    bezierVertex(198, 206, 97, 154, 101, 281)
    endShape()
    beginShape()
    translate(-75, 0)
    vertex(106, 279)
    bezierVertex(74, 146, -5, 250, -37, 271)
    bezierVertex(96, 190, 75, 279, 100, 282)
    endShape()
    popMatrix()


# ==================================================================== icons ==
def draw_hearts():
    pushMatrix()
    translate(8, 0)
    scale(0.3)
    for i in range(0, 124, 6):
        fill(222, 22, 22, 20)
        noStroke()
        ellipse(135, 163, 135 + i, 152 + i)

    pushMatrix()
    translate(0, -50)
    stroke(48, 48, 48)
    strokeWeight(7)
    fill(227, 38, 38)
    beginShape()
    for px, py in ((134, 142), (92, 94), (56, 129), (28, 199), (39, 264),
                   (147, 335), (222, 259), (239, 195), (204, 131), (173, 94)):
        vertex(px, py)
    endShape(CLOSE)

    pushMatrix()
    translate(0, 0)
    noStroke()
    fill(0, 0, 0, 20)
    beginShape()
    for px, py in ((134, 142), (92, 96), (59, 129), (31, 199), (41, 264), (147, 333)):
        vertex(px, py)
    endShape(CLOSE)
    popMatrix()
    popMatrix()
    popMatrix()


def draw_emerald():
    pushMatrix()
    translate(7, 7)
    rectMode(CENTER)
    for i in range(15):
        fill(58, 209, 50, 20)
        noStroke()
        rect(25, 35, 50 + i, 70 + i, 20)
    rectMode(CORNER)

    stroke(48, 171, 40)
    strokeWeight(1)
    fill(58, 209, 50)
    rect(0, 0, 50, 70, 10)
    fill(61, 199, 52)
    noStroke()
    rect(2, 0, 23, 70, 5)
    popMatrix()


def draw_money():
    pushMatrix()
    translate(35, 35)
    rectMode(CENTER)
    for i in range(15):
        fill(255, 216, 97, 20)
        noStroke()
        ellipse(0, 0, 50 + i, 52 + i)

    stroke(255, 187, 69)
    strokeWeight(1)
    fill(255, 211, 36)
    ellipse(0, 0, 50, 50)
    fill(255, 217, 64)
    noStroke()
    rotate(45)
    rect(0, 0, 25, 25)
    popMatrix()
    rectMode(CORNER)


def draw_deletes():
    # Baked by the original loader but never actually blitted anywhere.
    pushMatrix()
    translate(15, 15)
    rectMode(CENTER)
    fill(214, 30, 30)
    noStroke()
    ellipse(0, 0, 30, 30)
    fill(255, 255, 255)
    rect(0, -6, 17, 3, 10)
    rect(0, 6, 11, 3, 10)
    rect(-4, 1, 3, 10, 10)
    rect(0, 1, 3, 10, 10)
    rect(4, 1, 3, 10, 10)
    popMatrix()


# ================================================================= bullets ===
def _glow_ball(core, ring, shard, quad_pts):
    pushMatrix()
    translate(78, 77)
    noStroke()
    fill(*core)
    ellipse(0, 0, 60, 60)
    for i in range(22):
        stroke(ring[0], ring[1], ring[2], 20)
        noFill()
        strokeWeight(10)
        ellipse(0, 0, 50 + i, 50 + i)
    i = 0
    while i < 360:
        s = 0.0
        while s < 1.0:
            pushMatrix()
            translate(rnd(-12, 12), 0)
            rotate(i)
            scale(s)
            fill(shard[0], shard[1], shard[2], 20)
            noStroke()
            quad(*quad_pts)
            popMatrix()
            s += 0.1
        i += 62
    popMatrix()


def draw_snowBullet():
    _glow_ball((184, 244, 255), (150, 234, 255), (199, 233, 255),
               (0, 0, 67, 51, 0, 40, 74, 7))


def draw_snowBulletUltimate():
    _glow_ball((0, 52, 61), (0, 82, 204), (46, 46, 46),
               (0, 0, 67, 51, 0, 40, 74, 7))


def draw_smolsnowBullet():
    _glow_ball((0, 12, 145), (0, 157, 255), (0, 187, 255),
               (0, 0, 67, 51, 0, 40, 74, 7))


def draw_iceBullet():
    _glow_ball((87, 202, 255), (199, 234, 255), (163, 230, 255),
               (70, 0, -62, 51, 0, 40, 74, 7))


def draw_enemyBlt():
    _glow_ball((255, 227, 89), (255, 180, 51), (255, 124, 36),
               (16, 57, -62, 51, 0, 40, 74, 7))


# ------------------------------------------------------------------------- --
def draw_frozen():
    """Extracted from Enemies.looks() so the ice cage can be a sprite too."""
    fill(189, 221, 255, 100)
    stroke(115, 197, 255, 80)
    strokeWeight(10)
    pushMatrix()
    # original did translate(-90,-90); scale(0.9) around the enemy origin, so on
    # a 180x180 sprite the same geometry lands centred with no translate at all.
    scale(0.9)
    beginShape()
    for px, py in ((131, 155), (114, 152), (108, 164), (85, 147), (62, 150),
                   (51, 125), (56, 92), (49, 63), (71, 41), (94, 46),
                   (119, 38), (144, 56), (142, 84), (151, 104), (136, 122),
                   (144, 140)):
        vertex(px, py)
    endShape(CLOSE)
    popMatrix()


# =============================================================== backdrops ===
def _snow_scene():
    """The shared body of backdropfull / backdrop1."""
    rectMode(CORNER)
    # sky
    noStroke()
    fill(184, 225, 255)
    rect(0, 0, WIDTH, HEIGHT)
    fill(255, 255, 255, 30)
    triangle(600, 80, 600, 15, 200, 30)
    triangle(600, 80, 600, 200, -70, 90)
    triangle(600, 240, 0, 340, 0, 200)
    triangle(600, 305, 0, 340, 0, 440)

    # moon
    noStroke()
    fill(232, 251, 255)
    ellipse(340, 230, 75, 75)
    fill(255, 255, 255, 50)
    ellipse(340, 230, 90, 95)
    ellipse(340, 230, 105, 100)
    ellipse(340, 230, 120, 125)
    ellipse(340, 230, 135, 130)
    fill(255, 255, 255, 30)
    ellipse(340, 230, 150, 155)

    _mountains((232, 250, 255), (201, 236, 255), (161, 206, 245))
    _far_ground((232, 250, 255), (204, 235, 255))
    _mid_ground((196, 225, 255), (173, 210, 255))

    trees(430, 418, -0.40, 0.20)
    trees(140, 420, 0.20, 0.15)
    trees(300, 427, 0.13, 0.10)

    _tree_shadows(color(10, 42, 171, 30))

    pushMatrix()
    pushStyle()
    translate(0, 330)
    scale(0.45, 0.45)
    _foreground((237, 252, 255), (43, 158, 230, 40), (0, 145, 255, 50), (63, 130, 212, 30))
    trees()
    popStyle()
    popMatrix()


def _mountains(c1, c2, c3):
    noStroke()
    fill(*c1)
    beginShape()
    vertex(220, 455)
    vertex(220, 437)
    bezierVertex(305, 407, 320, 407, 400, 370)
    bezierVertex(430, 360, 430, 370, 470, 387)
    bezierVertex(510, 393, 535, 350, 560, 330)
    bezierVertex(575, 320, 590, 327, 600, 340)
    vertex(600, 455)
    endShape()

    fill(*c2)
    beginShape()
    vertex(245, 455)
    vertex(245, 437)
    bezierVertex(305, 417, 320, 407, 400, 380)
    bezierVertex(430, 377, 430, 380, 470, 403)
    bezierVertex(500, 393, 535, 350, 550, 340)
    bezierVertex(575, 335, 590, 350, 600, 375)
    vertex(600, 455)
    endShape()

    fill(*c3)
    beginShape()
    vertex(290, 455)
    vertex(290, 440)
    bezierVertex(340, 430, 360, 415, 385, 415)
    bezierVertex(403, 417, 373, 460, 490, 405)
    bezierVertex(515, 405, 470, 423, 490, 440)
    vertex(555, 440)
    bezierVertex(560, 433, 555, 420, 520, 395)
    bezierVertex(560, 400, 575, 420, 600, 430)
    vertex(600, 455)
    endShape()


def _far_ground(c1, c2):
    noStroke()
    fill(*c1)
    beginShape()
    vertex(0, 600)
    vertex(0, 440)
    bezierVertex(260, 425, 390, 455, 600, 455)
    vertex(600, 600)
    endShape()

    fill(*c2)
    beginShape()
    vertex(0, 450)
    bezierVertex(50, 445, 115, 447, 135, 450)
    vertex(115, 443)
    bezierVertex(140, 440, 195, 437, 280, 443)
    vertex(260, 445)
    vertex(440, 455)
    bezierVertex(280, 457, 100, 455, 0, 470)
    endShape()


def _mid_ground(c1, c2):
    noStroke()
    fill(*c1)
    beginShape()
    vertex(0, 600)
    vertex(0, 475)
    bezierVertex(127, 465, 245, 460, 305, 460)
    bezierVertex(323, 465, 287, 470, 297, 475)
    bezierVertex(390, 485, 430, 465, 600, 460)
    vertex(600, 600)
    endShape()

    fill(*c2)
    beginShape()
    vertex(0, 490)
    vertex(0, 483)
    bezierVertex(50, 477, 150, 457, 230, 470)
    bezierVertex(227, 477, 140, 467, 110, 483)
    bezierVertex(145, 487, 220, 480, 267, 467)
    bezierVertex(267, 470, 240, 480, 243, 483)
    bezierVertex(247, 485, 253, 485, 253, 487)
    bezierVertex(200, 497, 70, 485, 0, 490)
    endShape()

    beginShape()
    vertex(600, 515)
    bezierVertex(510, 500, 330, 465, 600, 483)
    endShape()


def _tree_shadows(col):
    fill(col)
    beginShape()
    vertex(172, 475)
    vertex(170, 475)
    bezierVertex(155, 480, 143, 487, 137, 493)
    vertex(177, 495)
    bezierVertex(177, 493, 180, 490, 175, 487)
    bezierVertex(187, 475, 163, 480, 170, 480)
    endShape()

    beginShape()
    vertex(321, 465)
    vertex(320, 465)
    vertex(315, 470)
    bezierVertex(297, 470, 285, 503, 310, 483)
    bezierVertex(320, 480, 320, 475, 320, 473)
    vertex(317, 470)
    endShape()

    beginShape()
    vertex(370, 493)
    vertex(365, 493)
    vertex(360, 497)
    bezierVertex(350, 500, 350, 500, 345, 503)
    vertex(385, 507)
    bezierVertex(383, 500, 370, 497, 367, 500)
    endShape()


def _foreground(c1, c2, c3, c4):
    noStroke()
    fill(*c1)
    beginShape()
    vertex(0, 600)
    vertex(0, 380)
    bezierVertex(180, 350, 360, 370, 710, 375)
    bezierVertex(850, 400, 1167, 420, 1335, 430)
    vertex(1335, 600)
    endShape()

    fill(*c2)
    beginShape()
    vertex(0, 600)
    vertex(0, 400)
    bezierVertex(50, 390, 100, 365, 150, 370)
    bezierVertex(180, 385, 170, 400, 190, 420)
    bezierVertex(230, 430, 260, 380, 480, 385)
    bezierVertex(520, 383, 488, 370, 480, 370)
    vertex(590, 373)
    bezierVertex(550, 390, 520, 400, 500, 450)
    bezierVertex(520, 470, 580, 450, 660, 410)
    bezierVertex(690, 400, 715, 405, 730, 410)
    bezierVertex(745, 415, 705, 440, 695, 455)
    bezierVertex(880, 450, 870, 390, 1200, 460)
    vertex(1335, 480)
    vertex(1335, 600)
    endShape()

    fill(*c3)
    beginShape()
    vertex(0, 600)
    vertex(0, 530)
    bezierVertex(30, 515, 120, 490, 170, 500)
    bezierVertex(190, 505, 190, 530, 175, 555)
    bezierVertex(170, 565, 180, 575, 210, 580)
    bezierVertex(290, 580, 420, 550, 930, 500)
    bezierVertex(1100, 490, 930, 560, 883, 585)
    bezierVertex(1150, 532, 1180, 543, 1335, 530)
    vertex(1335, 600)
    endShape()

    fill(*c4)
    beginShape()
    vertex(0, 587)
    vertex(0, 425)
    bezierVertex(5, 423, 30, 417, 35, 420)
    bezierVertex(0, 400, 30, 363, 130, 387)
    vertex(150, 375)
    vertex(160, 375)
    vertex(140, 395)
    bezierVertex(260, 457, 40, 577, 0, 587)
    endShape()


def draw_backdropfull():
    _snow_scene()


def draw_backdrop2full(n=700, lo=0, hi=600):
    background(46, 15, 0)
    for _ in range(n):
        fill(255, 169 + rnd(-130, 20), 20, 20)
        noStroke()
        ellipse(rnd(lo, hi), rnd(-30, 641), 100, 100)


def draw_backdrop2():
    draw_backdrop2full(500, 300, 897)


def draw_backdrop3full():
    rectMode(CORNER)
    noStroke()
    fill(115, 194, 255)
    rect(0, 0, WIDTH, HEIGHT)
    fill(204, 243, 255, 30)
    triangle(600, 80, 600, 15, 200, 30)
    triangle(600, 80, 600, 200, -70, 90)
    triangle(600, 240, 0, 340, 0, 200)
    triangle(600, 305, 0, 340, 0, 440)

    noStroke()
    fill(255, 204, 122)
    ellipse(340, 230, 75, 75)
    fill(255, 191, 112, 50)
    ellipse(340, 230, 90, 95)
    ellipse(340, 230, 105, 100)
    ellipse(340, 230, 120, 125)
    ellipse(340, 230, 135, 130)
    fill(255, 192, 84, 30)
    ellipse(340, 230, 150, 155)

    _mountains((79, 194, 56), (78, 176, 46), (98, 186, 63))
    _far_ground((65, 163, 33), (64, 89, 255))
    _mid_ground((196, 225, 255), (86, 184, 71))

    trees(430, 418, -0.40, 0.20)
    trees(140, 420, 0.20, 0.15)
    trees(300, 427, 0.13, 0.10)

    _tree_shadows(color(0, 0, 0, 30))

    pushMatrix()
    pushStyle()
    translate(0, 330)
    scale(0.45, 0.45)
    _foreground((106, 196, 76), (78, 153, 28, 40), (67, 166, 58, 50), (24, 110, 20, 30))
    trees()
    popStyle()
    popMatrix()


def draw_backdrop3():
    background(82, 171, 91)
    fill(71, 158, 80)
    rectMode(CORNER)
    noStroke()
    for i in range(0, 500, 80):
        rect(i, 100, 3, 400)
    for i in range(6):
        rect(0, 100 + i * 80, 480, 3)
    for _ in range(0, WIDTH, 5):
        fill(71, 158, 80, 50)
        rect(rnd(0, WIDTH), 0, 5, 600)
