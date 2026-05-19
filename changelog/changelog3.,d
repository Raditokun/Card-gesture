# Changelog — Card Battler: Game Board Upgrade

## 2026-05-19 — `main.py` — Game Board & Multi-Card Drag-Drop

### Summary
Upgraded the single-card gesture playground into a proper game board with two zones, five cards, z-index-aware grabbing, and smart drop validation with snap-back.

### File: [main.py](file:///d:/RADIT%20Files/code/py/main.py)

---

### What changed

#### 1. Drop Zones
Two `pygame.Rect` areas define the board layout:

| Zone | Rect | Purpose |
|---|---|---|
| **Play Zone** | `(40, 30, 1200, 440)` | Upper/mid area — valid card placement |
| **Hand Zone** | `(40, 490, 1200, 200)` | Bottom strip — the player's hand |

Both are drawn with a semi-transparent fill (via a temporary `SRCALPHA` surface) and a coloured border. The Play Zone is teal-tinted; the Hand Zone is purple-tinted.

#### 2. Card Class Upgrades
```diff
 class Card:
+    home_x, home_y   # remembers where the card "belongs"
+    def snap_to_home()  # instantly moves back to home position
+    @property center    # returns (cx, cy) tuple for drop validation
```
- `home_x` / `home_y` are set in `__init__` to the card's starting position.
- On a valid Play Zone drop, `home_x/y` update to the new board location.
- On an invalid drop, `snap_to_home()` teleports the card back.

#### 3. Multiple Cards + Z-Index Grabbing
Five cards are spawned evenly inside the Hand Zone via `build_hand()`:
```python
cards: list[Card] = build_hand(NUM_CARDS)  # NUM_CARDS = 5
```

**Grab logic uses `reversed()`:**
```python
for card in reversed(cards):
    if card.collidepoint(cursor_x, cursor_y):
        dragged_card = card
        break  # only grab ONE card
```

#### 4. Valid Drop Logic
```
Release pinch →
  card center inside PLAY_ZONE_RECT?
    YES → update home_x/home_y to current position (card stays)
    NO  → snap_to_home() (card returns to hand)
  Move card to end of list (renders on top)
```

---

### Why `reversed()` is the standard for z-index clicking

When you draw a list of objects in order (`cards[0]` first, `cards[-1]` last), the **last item** in the list is visually "on top" — it's painted over everything else. This is known as the **painter's algorithm**.

To match this visual stacking when checking clicks, you need to test the top-most object first:

```python
# ✅ Correct: check top-most card first
for card in reversed(cards):
    if card.collidepoint(cx, cy):
        grab(card)
        break

# ❌ Wrong: checks bottom card first — grabs a hidden card
for card in cards:
    if card.collidepoint(cx, cy):
        grab(card)
        break
```

`reversed()` returns a reverse iterator — it **does not** copy or mutate the list. It's O(1) memory and idiomatic Python. The `break` after the first hit is equally critical: without it, overlapping cards could all get grabbed in a single frame.

> [!TIP]
> After dropping a card, we do `cards.remove(card); cards.append(card)` to move it to the end of the list. This ensures the most recently interacted card always renders on top — a standard UX pattern in any drag-and-drop interface.
