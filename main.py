"""
AVAWARS - Python / pygame port of the Khan Academy ProcessingJS original
by Corin Fist Productions (2021).

Runs on the desktop:      python main.py
Runs in a browser:        pygbag .        (see README)

The loop is `async` and yields once per frame so the same file works unmodified
under pygbag/WebAssembly, where a blocking `while True` would freeze the tab.
"""
from __future__ import annotations

import asyncio
import sys

import pygame

import state


async def main():
    pygame.init()
    pygame.display.set_caption("AVAWARS")
    screen = pygame.display.set_mode((state.WIDTH, state.HEIGHT))
    clock = pygame.time.Clock()

    # imported after display init so font/Surface creation is legal
    import scenes

    arrow = pygame.SYSTEM_CURSOR_ARROW
    hand = pygame.SYSTEM_CURSOR_HAND
    cursor_now = arrow

    def set_cursor(c):
        # Not every backend can make system cursors (headless SDL, some
        # browsers).  A missing hand pointer must never take the game down.
        try:
            pygame.mouse.set_cursor(c)
            return True
        except Exception:
            return False

    cursors_ok = set_cursor(arrow)

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                state.keys.codes.add(ev.key)
                if ev.unicode:
                    state.keys.chars.add(ev.unicode.lower())
                if ev.key == pygame.K_ESCAPE:
                    running = False
            elif ev.type == pygame.KEYUP:
                state.keys.codes.discard(ev.key)
                if ev.unicode:
                    state.keys.chars.discard(ev.unicode.lower())
                else:
                    # some layouts report no unicode on keyup
                    name = pygame.key.name(ev.key)
                    state.keys.chars.discard(name)
            elif ev.type == pygame.MOUSEBUTTONUP:
                # Processing's mouseClicked fires on release
                state.clicked = True
                state.mouse_button = {1: "LEFT", 2: "CENTER", 3: "RIGHT"}.get(
                    ev.button, "LEFT")
            elif ev.type == pygame.WINDOWFOCUSLOST:
                state.keys.clear()

        state.mouse_x, state.mouse_y = pygame.mouse.get_pos()
        state.want_hand = False

        scenes.manage_scenes(screen)

        if cursors_ok:
            want = hand if state.want_hand else arrow
            if want != cursor_now:
                cursor_now = want
                set_cursor(want)

        state.clicked = False
        state.frame_count += 1

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
