# Changelog — Card Battler: Gesture Playground Integration

## 2026-05-19 — `main.py` — Full Rewrite

### Summary
Replaced the old Pyglet rhythm-game `main.py` (371 lines, pose scoring, beat maps) with a clean Pygame-based gesture playground that integrates the new `HandTracker` from `gesture.py`.

### File: [main.py](file:///d:/RADIT%20Files/code/py/main.py)

| Aspect | Old (Rhythm Game) | New (Card Battler Playground) |
|---|---|---|
| Framework | Pyglet + pyglem wrapper | Pygame |
| Input | MediaPipe Pose (body landmarks) | MediaPipe Hands via `HandTracker` |
| Gameplay | Beat map → pose scoring → combo | Drag-and-drop card with pinch gesture |
| Rendering | Pyglet sprites + text labels | `pygame.draw` primitives |

---

### What was added

#### 1. HandTracker Integration
```python
tracker = HandTracker(screen_width=SCREEN_W, screen_height=SCREEN_H)
# … game loop …
cursor_x, cursor_y, is_clicking = tracker.get_cursor_state()
# … on exit …
tracker.release()
```
The tracker is created once before the loop and released in the cleanup section after the loop ends, guaranteeing the webcam is freed even on `ESC` or window-close.

#### 2. Visual Cursor
A filled circle drawn at the smoothed `(cursor_x, cursor_y)`:
- **White** (`220, 225, 240`) when the hand is open
- **Red** (`230, 60, 70`) when pinching

A dark ring is drawn on top to give the cursor a crisp outline against any background.

#### 3. Card Class
```python
class Card:
    x, y, width, height, is_dragging
    rect      → pygame.Rect (property, rebuilt every access)
    collidepoint(px, py) → bool
    draw(surface)        → renders filled rect + border + label
```
The card is centred on screen at startup. Its `draw()` method changes fill colour when `is_dragging` is `True` so the player gets immediate visual feedback.

#### 4. Drag & Drop Logic
```
if is_clicking:
    if card.is_dragging:          → keep moving card to cursor
    elif card.collidepoint(…):    → start dragging
else:
    card.is_dragging = False      → drop
```
The card's position is set so the cursor sits at the card's centre (`card.x = cx - width/2`), preventing the card from jumping to a corner on grab.

---

### How `collidepoint()` works vs. manual AABB

Pygame's `Rect.collidepoint(px, py)` is a C-implemented axis-aligned bounding-box (AABB) test. Conceptually it does exactly this:

```python
# Manual AABB — what you'd write by hand:
def collides(rect, px, py):
    return (rect.left <= px < rect.right and
            rect.top  <= py < rect.bottom)
```

The Pygame version is **functionally identical** but:

| | Manual AABB | `collidepoint()` |
|---|---|---|
| **Performance** | Pure Python — 4 comparisons per call | C extension — same 4 comparisons, but at native speed |
| **Edge semantics** | You choose `<=` vs `<` | Uses `<=` for left/top, `<` for right/bottom (standard half-open interval) |
| **Error surface** | Easy to swap `x`/`y` or use wrong edges | Single call, no room for off-by-one bugs |
| **Readability** | Verbose | Self-documenting |

> [!TIP]
> For simple rectangular hit-tests, always prefer `collidepoint()`. Reserve manual math for non-rectangular shapes (circles, polygons) or rotated cards in the future.

---

### HUD Status Bar
A single line at the bottom of the screen shows:
```
Cursor: (640, 360)  |  PINCH  |  Card: DRAGGING
```
This makes it easy to debug tracking without needing a terminal.
