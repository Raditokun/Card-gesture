# Changelog — Card Battler: TCG Card Rendering

## 2026-05-19 — `main.py` — Card Data & Visual Upgrade

### Summary
Upgraded blank "CARD" rectangles into fully rendered trading-card faces with **name**, **cost badge**, **ATK/HP stats**, an **art placeholder**, and **per-card base colours** driven by a deck data structure.

### File: [main.py](file:///d:/RADIT%20Files/code/py/main.py)

---

### What changed

#### 1. Deck Data Structure
A top-level `DECK_DATA` list of 5 dictionaries defines the starting hand:

| Card | Cost | ATK | HP | Colour |
|---|---|---|---|---|
| Rendang of Ruin | 5 | 8 | 8 | Dark red |
| DRS Overtake | 3 | 6 | 2 | Navy blue |
| Cryomancer's Chill | 4 | 4 | 6 | Ice blue |
| Spicy Garlic Chicken | 2 | 3 | 1 | Orange |
| Buzzer Beater | 4 | 5 | 5 | Gold |

#### 2. Card Class Upgrades

**New `__init__` signature:**
```python
Card(x, y, data: dict, width=120, height=180)
```
Stores `name`, `cost`, `atk`, `hp`, and `base_color` from the data dict.

**Font singleton pattern:**
```python
Card.init_fonts()  # called once after pygame.init()
```
Fonts are class-level attributes, created once and shared by all instances. This avoids re-creating `SysFont` objects on every `draw()` call — a common Pygame performance pitfall.

**Card face layout (120×180 px):**
```
┌──────────────────────┐
│ (5) Card Name        │  ← cost badge (circle) + name text
│ ┌──────────────────┐ │
│ │                  │ │  ← art placeholder (darker rect)
│ │                  │ │
│ │                  │ │
│ └──────────────────┘ │
│ ⚔8              ♥8  │  ← ATK (red) and HP (green) badges
└──────────────────────┘
```

- **Cost badge** — purple circle in the top-left corner, large bold number
- **Name** — white bold text, auto-truncated with `…` if it overflows
- **Art placeholder** — darkened inner rectangle (will hold card art later)
- **ATK** — red circle, bottom-left
- **HP** — green circle, bottom-right
- **Drag highlight** — `_brighten()` lightens the base colour by 35 when dragging

#### 3. Name Truncation
Long names like "Spicy Garlic Chicken" would overflow the 120px card width. The `draw()` method measures the rendered text width and progressively trims characters, appending `…`, until it fits within `card_width - 36px` (leaving room for the cost badge).

#### 4. `build_hand()` Update
```diff
-def build_hand(num_cards: int) -> list[Card]:
+def build_hand(deck: list[dict]) -> list[Card]:
```
Now iterates over the deck data list and passes each dict to the `Card` constructor. Card count is derived from `len(deck)` instead of a separate constant.

---

### What stayed the same
- All drag & drop logic (z-index grabbing, drop validation, snap-to-home)
- Zone rendering (Play Zone / Hand Zone)
- Cursor rendering with pinch colour feedback
- HUD status bar (now shows the dragged card's **name** instead of just "DRAGGING")
