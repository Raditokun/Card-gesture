# Changelog — Soaring Caraka: Menu System

## 2026-05-19 — `main.py` — Gesture-Controlled UI Menus

### Summary
Implemented a full 4-state menu system navigated entirely by hand gestures. The game is now titled **"Soaring Caraka"**.

### File: [main.py](file:///d:/RADIT%20Files/code/py/main.py)

---

### What changed

#### 1. `GameState` Enum
```python
class GameState(Enum):
    MENU        = auto()
    DECK_SELECT = auto()
    TUTORIAL    = auto()
    PLAYING     = auto()
```
Replaces the old `STATE_PLAYING = "PLAYING"` string constant. Using an enum prevents typos and gives IDE autocompletion.

#### 2. `UIButton` Class
```python
class UIButton:
    rect: pygame.Rect
    label: str
    hovered: bool
    update_hover(cx, cy)
    draw(surface)
```
- Highlights with `COL_BTN_HOVER` when the cursor is inside the rect.
- Renders a rounded rectangle with centred text — ready to be swapped for PNG assets later.

#### 3. Rising-Edge Click Detection
```python
prev_clicking = is_clicking                       # save last frame
cursor_x, cursor_y, is_clicking = tracker.get_cursor_state()
click_rising = is_clicking and not prev_clicking  # True for ONE frame only
```

**Why this matters:** Without rising-edge detection, a button press fires on *every frame* the player's fingers are pinched — potentially toggling states dozens of times per second. The rising-edge pattern ensures a click registers **once**, on the frame the pinch first begins.

```
Frame:     1    2    3    4    5    6    7
Pinch:     ─    ─    ■    ■    ■    ─    ─
Raw:                 ✓    ✓    ✓              ← fires 3 times
Rising:              ✓                        ← fires ONCE ✓
```

#### 4. Screen Layouts

| State | Content | Navigation |
|---|---|---|
| **MENU** | Title "SOARING CARAKA", subtitle, 3 buttons (START DUEL, DECK, TUTORIAL), hint text | Pinch buttons → change state. ESC → quit. |
| **DECK_SELECT** | Heading, card fan preview of current deck, placeholder text, BACK button | BACK or ESC → MENU |
| **TUTORIAL** | Heading, 7-line how-to-play text, BACK button | BACK or ESC → MENU |
| **PLAYING** | Play Zone, Hand Zone, draggable cards, HUD status bar | ESC → MENU |

#### 5. Cursor Always On Top
```python
# After ALL state-specific drawing is done:
draw_cursor(screen, cx, cy, is_clicking)
pygame.display.flip()
```
The cursor `draw_cursor()` call was moved **outside** the state `if/elif` block, after all state rendering. This guarantees the cursor circle is always the last thing painted, so it's never hidden behind cards, buttons, or zone overlays.

#### 6. ESC Key Behaviour
- **From MENU** → quits the application
- **From any other state** → returns to MENU (soft escape, doesn't kill the game)

---

### What stayed the same
- Card class (data, rendering, drag & drop logic)
- Zone rendering and drop validation
- `build_hand()` deck layout
- All gesture.py integration
