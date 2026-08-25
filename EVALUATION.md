# Evaluating the original AVAWARS (Thank you to Claude for the Conversion and Evaluation here)

Notes from porting ~2,600 lines of Khan Academy ProcessingJS to Python.

---

## 1. Architecture

The program is better structured than most Khan Academy work of its era. It has
a real scene graph (`Manage_scenes` + a string `scene` variable), prototype-based
entity classes with a consistent `update()` / `draw()` split, an `Admin`
singleton holding economy and HUD state, and a genuine asset pipeline. The
banner-comment section headers make a 2,600-line single file navigable, which is
not nothing.

Four things stand out as genuinely good instincts:

**The `Trans` transition.** Grabbing the framebuffer, spinning it, then sliding
it off screen while the next scene swaps in underneath. It costs one screenshot
and hides all scene-setup latency. This ported directly — `get(0,0,width,height)`
became `screen.copy()`.

**Data-driven avatars.** Both `Selection` and `Tiles` switch on a `type` string,
so all five defenders share one code path. Adding a sixth would mean touching
four switch blocks — not ideal, but far better than five parallel classes.

**Growth-stage art reuse.** Frostine's five stages are strictly additive: seed →
+ leaf → + ears/veins → + two more leaves → + wings/horn. The seedling's leaf is
literally the same code as the tree's leaf, called under a different transform.
In the port I hoisted those into `_frost_leaf()`, `_frost_ears()`,
`_frost_body_*()`, and the five stages collapsed to a few lines each. The
original had them copy-pasted, which is why `Frostultimate` is 200 lines.

**Difficulty as one number.** `admin.timer` decays 20 → 5 at 0.002/frame and
feeds both spawn cadence and `enemyLevel = 6/(timer/4)`, so enemy tier ramps
from 1 to ~5 across a match. One variable, whole curve. Elegant.

Where it's weak: `Admin` is a god object mixing economy, HUD layout, scroll
physics and cursor state; `Selection.cost` is assigned inside its *draw* method,
so cost is undefined until the button has been rendered once; and mouse-hover
tests are duplicated inline in five classes instead of sharing a helper.

---

## 2. The image caching — was it worth it?

**Yes, decisively. It's the single most important decision in the program.**
But the *mechanism* was the weak part, not the idea.

### What it did

`img` starts as an object of *functions*. The `load` scene calls one per frame,
and each function draws to the canvas and returns `get(x, y, w, h)` — a `PImage`
snapshot — which then overwrites the function in the same slot. After loading,
`img.FrostyTree` is no longer a function, it's a bitmap, and everything
downstream is `image()` blitting.

### The measurements

I instrumented my shim to count polygon rasterisations and vertices while baking
all 26 assets:

| Asset | Shapes | Vertices |
|---|---:|---:|
| `FrostyUltimate` | 50 | 3,631 |
| `FrostyTree` | 36 | 2,777 |
| `backdropfull` | 35 | 2,726 |
| `snowBullet` | 89 | 1,506 |
| `backdrop2full` | 700 | 31,500 |
| **All 26 assets** | **2,099** | **82,393** |

Now price a busy frame if none of that were cached — 30 tiles of freezers (three
sprites each), 12 tier-5 Vortans, 40 bullets in flight, one background:

```
live vector rendering   ≈ 4,900 polygon fills + strokes per frame
cached blitting         ≈   143 blits per frame
```

At 60 fps that's **~294,000 polygon operations per second versus ~8,600 blits**,
a ~34× reduction in work, and the polygon path additionally has to tessellate
every bezier. Khan Academy's ProcessingJS is a canvas-2D interpreter running on
a shim over a shim; without this cache the game would not have held 60 fps with
a full board. In Python it would be flatly impossible — my port sustains ~400 fps
headless with a full board precisely because of it.

The glow effects make the case even harder. `snowBullet` is 89 shapes: 22
concentric stroked ellipses plus 60 alpha-blended shards. Every bullet on screen
would pay that cost, every frame. Baked once, a bullet is one rotated blit.

**So: keep the pre-rendering. It is not an optimisation, it is a requirement.**

### What was wrong with the mechanism

1. **It rendered to the visible canvas.** `get()` reads the framebuffer, so
   assets had to be drawn on screen and then hidden. Hence the `background(0,0)`
   call at the top of `load.draw()` and the opaque green `background()` painted
   over it immediately after. That's a workaround for a self-inflicted problem.
2. **Assets were clipped to the canvas.** `get(0,0,400,400)` means anything a
   character draws beyond x=400 is silently lost. `Vortanseedling` genuinely
   loses geometry to this.
3. **Positioning was manual and brittle.** Each function hand-tunes an offset
   (`Frostsapling(205, 185, 3)`) so the art lands inside the capture rect. Change
   the art and you re-tune the magic numbers.
4. **`backdrop1` re-renders `backdropfull` in full** just to `get(300,0,300,600)`
   a half of it. Identical geometry, rendered twice.
5. **Baked randomness varied per run.** `backdrop2full` scatters 700 random
   ellipses. Baking them freezes the noise — good — but each *session* got
   different art.
6. **`img.deletes` is baked and never used.** Dead weight in the loading bar.

### What I did instead

Same idea, better plumbing:

* Render to **off-screen `SRCALPHA` surfaces**. No canvas flash, no hiding hack,
  no clipping to the display rect.
* **Supersample and downscale** — characters at 2×, icons and bullets at 3×,
  backdrops at 1×. That buys antialiasing for free, which `get()` could never do.
* **Crop `backdrop1` from `backdropfull`** instead of re-rendering it. Exactly
  equivalent, and free.
* **Seed the RNG per asset** so the noise fields are identical every run.
* **Bake the frozen-enemy ice cage** as a 27th sprite. The original redrew a
  16-vertex stroked polygon per frozen enemy per frame; it's now a blit.
* Keep **one asset per frame**, which the original got right for a good reason
  and which matters even more under WebAssembly, where a blocking loop freezes
  the browser tab.

Total bake time in the port: **~160 ms** for all 26 assets. The original's
"Please be patient" screen plus its two-second artificial pause was generous.

### What should *not* be cached

Not everything. Three things are correctly live, and I kept them live:

* **Neon buttons** — the border radius and fill alpha animate continuously on
  hover. I cache them by *appearance* instead: quantise `fadeOut` into 16 buckets
  and bake one frame per bucket. 13 stroked rounded rects per button per frame
  became one blit.
* **Glow text** — `gtext()` stamps the string **36 times** per call. Baking every
  possible string is impossible (the money counter changes every frame), so it's
  cached by `(text, size, colour, alignment)` with LRU eviction. The HUD then
  costs three blits instead of 108 text draws.
* **Particles** — position and alpha are per-instance, but the *sprite* isn't.
  Circles are cached by (diameter, colour quantised to 4 bits) and tinted with
  per-surface alpha at blit time.

That's the general rule the original didn't articulate: **cache by appearance,
not by object.** Anything whose pixels depend only on a small set of discrete
parameters can be baked, even if it looks "dynamic".

---

## 3. Bugs found

Ported faithfully, because they define how the game plays:

| | |
|---|---|
| `this.dmg = random()` | Tier-1 Vortans deal 0–1 damage. Almost certainly meant `random(1,5)`. They're harmless. |
| `if (this.emerald === 30)` | Emeralds only drop on an exact roll of 30. Tier 1 (`random(10,30)`) rounds to 30 about 2% of the time; tier 3 (`random(30,32)`) ~⅓; tier 4 (`random(30,31)`) ~½; **tier 5 (`random(30,30)`) always**. An unintended but well-shaped reward curve. |
| Tile bullet radius of 10 | Enemy bullets move 8–13 px/frame, so they can step straight over a tile's hit circle. Defenders survive longer than intended. |
| `handleDeath` resets `health = 100` | Wrong for the type, but harmless — `setHealth()` runs on the next placement. |

Fixed, because they're defects rather than balance:

| | |
|---|---|
| `for (var i in en) { … en.splice(i,1) }` | Mutating an array while iterating it. Every removal skips the next entity's update for that frame. Now: iterate a copy, filter afterwards. |
| `Selection.cost` set in `images()` | Cost was `0` until the button first rendered, so the first frame let you buy anything free. Now a lookup table. |
| `Trans.grabbed` never initialised | Worked by accident (`undefined` is falsy). Now explicit. |
| Unbounded particles | 50 per enemy death with no cap. Soft-capped at 900. |

---

## 4. The trickiest part of the conversion

Three ProcessingJS behaviours the art silently depends on, all of which had to
be reproduced exactly or the sprites come out wrong:

**Degrees, not radians.** Khan Academy's ProcessingJS runs `rotate()`, `arc()`,
`sin()` and `cos()` in degrees. `Trans` spinning to `r >= 359` and `rotate(45)`
turning a square into a diamond confirm it.

**The CTM is applied at `endShape()`, not at `vertex()`.** `Vortantree` calls
`translate(-77,-2)` *in the middle* of a `beginShape()` block and expects the
whole shape to move — and expects the translate to persist afterwards, since
there's no `pushMatrix` around it. My shim buffers raw vertices and transforms
them all at `endShape()` time.

**One `curveVertex()` converts the entire shape to a spline.** This is the one
that bit me. ProcessingJS's `curveVertex()` sets an `isCurve` flag and then calls
`vertex()`; at `endShape()`, if that flag is set, the *whole* vertex array is
rendered as a single Catmull-Rom curve with the first and last points as guides —
and if there are fewer than four points, nothing draws at all. My first pass
treated stray `curveVertex` calls as ordinary vertices, and `Vortanseedling` came
out as a large flat triangle instead of a flame sprout. Matching the real
semantics fixed it, and the seedling now mirrors the Frostine seedling exactly,
which is obviously what the artist intended.

Two more small ones: `endShape()` without `CLOSE` still *fills* as a closed path
but doesn't *stroke* closed; and bare `trees()` calls inside the backdrops pass
`undefined` into `translate()`, producing a NaN matrix that draws nothing — dead
code that must stay dead, or three extra trees appear where they shouldn't.
