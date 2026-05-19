# Changelog — Card Battler Gesture System

## 2026-05-19 — `gesture.py` — Full Rewrite

### Summary
Replaced the old rhythm-game gesture module (MediaPipe **Pose** + background threading + 6-landmark body extraction) with a clean `HandTracker` class purpose-built for the Card Battler's cursor-and-click paradigm.

### File: [gesture.py](file:///d:/RADIT%20Files/code/py/gesture.py)

| Aspect | Old (Rhythm Game) | New (Card Battler) |
|---|---|---|
| MediaPipe model | `solutions.pose` (full body) | `solutions.hands` (hand only) |
| Architecture | Module-level globals + background thread | `HandTracker` class, single-threaded |
| Output | Dict of 6 body landmarks | `(cursor_x, cursor_y, is_clicking)` tuple |
| Coordinate origin | Pyglet (bottom-left, Y-up) | Pygame (top-left, Y-down) |
| Smoothing | None | Exponential moving average |

### Key Design Decisions

1. **Single-threaded by design** — The `get_cursor_state()` method is meant to be called once per Pygame frame. Since Pygame's loop is already synchronous, there's no need for a background thread. This avoids lock contention and shared-state complexity. If frame-rate becomes an issue later, threading can be re-introduced.

2. **Exponential Moving Average (EMA) smoothing** — Raw MediaPipe coordinates jitter frame-to-frame. The EMA formula `smooth += factor * (raw - smooth)` dampens this with a single tunable parameter (`smoothing`, default `0.3`). Lower values = smoother but laggier; higher values = snappier but shakier.

3. **Pinch = Click** — A "click" is registered when the Euclidean distance between the Index Finger Tip (landmark 8) and Thumb Tip (landmark 4) in normalised coordinates falls below `pinch_threshold` (default `0.05`). This is roughly a 5% frame-diagonal distance — tight enough to avoid accidental triggers.

4. **Configurable constructor** — `screen_width`, `screen_height`, `smoothing`, and `pinch_threshold` are all constructor parameters, making it trivial to tune without editing source code.

5. **Safe `release()` method** — Guards against double-release by checking `isOpened()` before releasing the camera, and closes the MediaPipe `Hands` instance cleanly.

### Usage Example (in `main.py`)
```python
from gesture import HandTracker

tracker = HandTracker(screen_width=1280, screen_height=720)

# Inside your Pygame loop:
cx, cy, clicking = tracker.get_cursor_state()

# On quit:
tracker.release()
```
