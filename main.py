import sys
from enum import Enum, auto
import pygame
from gesture import HandTracker


# ═════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═════════════════════════════════════════════════════════════════════════════

SCREEN_W = 1280
SCREEN_H = 720
FPS = 30

# ── Palette ──────────────────────────────────────────────────────────────────
COL_BG            = (18,  18,  24)
COL_CURSOR        = (220, 225, 240)
COL_CURSOR_PIN    = (230,  60,  70)
COL_HUD_TEXT      = (180, 185, 200)
COL_CARD_EDGE     = (220, 225, 235)

COL_PLAY_ZONE     = (30,  45,  55)
COL_PLAY_ZONE_BDR = (60,  95, 110)
COL_HAND_ZONE     = (35,  28,  45)
COL_HAND_ZONE_BDR = (80,  60, 110)

# Menu colours
COL_MENU_BG       = (12,  10,  22)
COL_TITLE          = (230, 200, 120)
COL_BTN_FILL      = (40,  38,  60)
COL_BTN_HOVER     = (65,  60, 100)
COL_BTN_BORDER    = (120, 110, 180)
COL_BTN_TEXT      = (220, 215, 240)
COL_SUBTITLE      = (140, 135, 160)

CURSOR_RADIUS     = 14
CURSOR_RING_WIDTH = 3

# Card dimensions
CARD_W = 120
CARD_H = 180

# Zone geometry
PLAY_ZONE_RECT = pygame.Rect(40, 30, SCREEN_W - 80, SCREEN_H - 280)
HAND_ZONE_RECT = pygame.Rect(40, SCREEN_H - 230, SCREEN_W - 80, 200)


# ═════════════════════════════════════════════════════════════════════════════
#  GAME STATES
# ═════════════════════════════════════════════════════════════════════════════

class GameState(Enum):
    MENU        = auto()
    DECK_SELECT = auto()
    TUTORIAL    = auto()
    PLAYING     = auto()


# ═════════════════════════════════════════════════════════════════════════════
#  CARD DECK DATA
# ═════════════════════════════════════════════════════════════════════════════

DECK_DATA = [
    {"name": "Rendang of Ruin",     "cost": 5, "atk": 8, "hp": 8,
     "color": (139, 0, 0)},
    {"name": "DRS Overtake",        "cost": 3, "atk": 6, "hp": 2,
     "color": (0, 0, 128)},
    {"name": "Cryomancer's Chill",  "cost": 4, "atk": 4, "hp": 6,
     "color": (173, 216, 230)},
    {"name": "Spicy Garlic Chicken","cost": 2, "atk": 3, "hp": 1,
     "color": (255, 140, 0)},
    {"name": "Buzzer Beater",       "cost": 4, "atk": 5, "hp": 5,
     "color": (218, 165, 32)},
]


# ═════════════════════════════════════════════════════════════════════════════
#  CARD CLASS
# ═════════════════════════════════════════════════════════════════════════════

class Card:
    """
    A draggable trading card with name, cost, atk, hp, and a base colour.

    Attributes
    ----------
    name        : str    – card title displayed at the top.
    cost        : int    – mana/energy cost (top-left badge).
    atk         : int    – attack stat (bottom-left).
    hp          : int    – health stat (bottom-right).
    base_color  : tuple  – RGB fill for the card body.
    x, y        : float  – current top-left position on screen.
    home_x/y    : float  – the position this card "belongs" to.
    is_dragging : bool   – True while the player is pinch-holding this card.
    """

    # Fonts are class-level so they're created once (after pygame.init)
    _font_name:  pygame.font.Font | None = None
    _font_stat:  pygame.font.Font | None = None
    _font_cost:  pygame.font.Font | None = None

    @classmethod
    def init_fonts(cls) -> None:
        """Call once after pygame.init() to set up shared fonts."""
        cls._font_name = pygame.font.SysFont("Consolas", 13, bold=True)
        cls._font_stat = pygame.font.SysFont("Consolas", 16, bold=True)
        cls._font_cost = pygame.font.SysFont("Consolas", 18, bold=True)

    def __init__(self, x: float, y: float, data: dict,
                 width: int = CARD_W, height: int = CARD_H):
        # Position / layout
        self.x = x
        self.y = y
        self.home_x = x
        self.home_y = y
        self.width = width
        self.height = height
        self.is_dragging = False

        # Card stats
        self.name:  str   = data["name"]
        self.cost:  int   = data["cost"]
        self.atk:   int   = data["atk"]
        self.hp:    int   = data["hp"]
        self.base_color: tuple = data["color"]

    # ── Convenience ─────────────────────────────────────────────────────

    @property
    def rect(self) -> pygame.Rect:
        """Return a Pygame Rect for collision / drawing."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    @property
    def center(self) -> tuple[int, int]:
        """Return the card's centre point."""
        return (int(self.x + self.width / 2),
                int(self.y + self.height / 2))

    def collidepoint(self, px: float, py: float) -> bool:
        """Check whether the point (px, py) falls inside this card."""
        return self.rect.collidepoint(int(px), int(py))

    def snap_to_home(self) -> None:
        """Instantly move the card back to its home position."""
        self.x = self.home_x
        self.y = self.home_y

    # ── Rendering ───────────────────────────────────────────────────────

    @staticmethod
    def _brighten(color: tuple, amount: int = 40) -> tuple:
        """Return a brighter version of an RGB tuple (clamped to 255)."""
        return tuple(min(255, c + amount) for c in color)

    def draw(self, surface: pygame.Surface) -> None:
        """Render a classic TCG-style card face onto *surface*."""
        r = self.rect
        pad = 6

        # ── Card body ────────────────────────────────────────────────────
        fill = self._brighten(self.base_color, 35) if self.is_dragging \
               else self.base_color
        pygame.draw.rect(surface, fill, r, border_radius=10)
        pygame.draw.rect(surface, COL_CARD_EDGE, r, width=2, border_radius=10)

        # ── Art placeholder (darker inner rectangle) ─────────────────────
        art_rect = pygame.Rect(
            r.left + pad, r.top + 32,
            r.width - pad * 2, r.height - 80,
        )
        darker = tuple(max(0, c - 40) for c in fill)
        pygame.draw.rect(surface, darker, art_rect, border_radius=4)

        # ── Cost badge (top-left circle) ─────────────────────────────────
        badge_cx = r.left + 16
        badge_cy = r.top + 16
        pygame.draw.circle(surface, (30, 20, 60), (badge_cx, badge_cy), 14)
        pygame.draw.circle(surface, (160, 140, 220), (badge_cx, badge_cy), 14, 2)
        cost_surf = self._font_cost.render(str(self.cost), True, (200, 190, 255))
        surface.blit(cost_surf, cost_surf.get_rect(center=(badge_cx, badge_cy)))

        # ── Card name (just right of the cost badge) ─────────────────────
        max_name_w = r.width - 36
        name_surf = self._font_name.render(self.name, True, (255, 255, 255))
        if name_surf.get_width() > max_name_w:
            truncated = self.name
            while len(truncated) > 4:
                truncated = truncated[:-1]
                name_surf = self._font_name.render(truncated + "…", True,
                                                   (255, 255, 255))
                if name_surf.get_width() <= max_name_w:
                    break
        surface.blit(name_surf, (r.left + 32, r.top + 8))

        # ── ATK badge (bottom-left) ─────────────────────────────────────
        atk_cx = r.left + 18
        atk_cy = r.bottom - 18
        pygame.draw.circle(surface, (150, 40, 40), (atk_cx, atk_cy), 14)
        pygame.draw.circle(surface, (255, 100, 100), (atk_cx, atk_cy), 14, 2)
        atk_surf = self._font_stat.render(str(self.atk), True, (255, 200, 200))
        surface.blit(atk_surf, atk_surf.get_rect(center=(atk_cx, atk_cy)))

        # ── HP badge (bottom-right) ─────────────────────────────────────
        hp_cx = r.right - 18
        hp_cy = r.bottom - 18
        pygame.draw.circle(surface, (30, 100, 50), (hp_cx, hp_cy), 14)
        pygame.draw.circle(surface, (80, 220, 120), (hp_cx, hp_cy), 14, 2)
        hp_surf = self._font_stat.render(str(self.hp), True, (180, 255, 200))
        surface.blit(hp_surf, hp_surf.get_rect(center=(hp_cx, hp_cy)))


# ═════════════════════════════════════════════════════════════════════════════
#  UI BUTTON HELPER
# ═════════════════════════════════════════════════════════════════════════════

class UIButton:
    """
    A simple rectangular button with hover highlight and label.

    Parameters
    ----------
    rect   : pygame.Rect  – clickable area.
    label  : str           – text drawn centred inside the button.
    font   : pygame.font.Font
    """

    def __init__(self, rect: pygame.Rect, label: str,
                 font: pygame.font.Font):
        self.rect = rect
        self.label = label
        self.font = font
        self.hovered = False

    def update_hover(self, cx: float, cy: float) -> None:
        """Update the hover flag based on cursor position."""
        self.hovered = self.rect.collidepoint(int(cx), int(cy))

    def draw(self, surface: pygame.Surface) -> None:
        """Render the button with optional hover highlight."""
        fill = COL_BTN_HOVER if self.hovered else COL_BTN_FILL
        pygame.draw.rect(surface, fill, self.rect, border_radius=8)
        pygame.draw.rect(surface, COL_BTN_BORDER, self.rect,
                         width=2, border_radius=8)
        txt = self.font.render(self.label, True, COL_BTN_TEXT)
        surface.blit(txt, txt.get_rect(center=self.rect.center))


# ═════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def build_hand(deck: list[dict]) -> list[Card]:
    """
    Create Card objects from *deck* data, spaced evenly along the
    centre of the Hand Zone.
    """
    num = len(deck)
    zone = HAND_ZONE_RECT
    total_cards_width = num * CARD_W
    gap = (zone.width - total_cards_width) / (num + 1)

    cards: list[Card] = []
    for i, data in enumerate(deck):
        cx = zone.left + gap * (i + 1) + CARD_W * i
        cy = zone.top + (zone.height - CARD_H) / 2
        cards.append(Card(cx, cy, data))
    return cards


def draw_zone(surface: pygame.Surface, rect: pygame.Rect,
              fill: tuple, border: tuple, label: str) -> None:
    """Draw a semi-transparent zone rectangle with a label."""
    zone_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    zone_surf.fill((*fill, 140))
    surface.blit(zone_surf, rect.topleft)
    pygame.draw.rect(surface, border, rect, width=2, border_radius=6)
    font = pygame.font.SysFont("Consolas", 14)
    tag = font.render(label, True, border)
    surface.blit(tag, (rect.left + 10, rect.top + 8))


def draw_cursor(surface: pygame.Surface, cx: int, cy: int,
                is_clicking: bool) -> None:
    """Draw the gesture cursor circle on top of everything."""
    color = COL_CURSOR_PIN if is_clicking else COL_CURSOR
    pygame.draw.circle(surface, color, (cx, cy), CURSOR_RADIUS)
    pygame.draw.circle(surface, COL_BG, (cx, cy),
                       CURSOR_RADIUS, CURSOR_RING_WIDTH)


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════════════════

def main():
    # ── Pygame init ──────────────────────────────────────────────────────
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Soaring Caraka")
    clock = pygame.time.Clock()

    # Initialise Card fonts (must happen after pygame.init)
    Card.init_fonts()

    # ── Fonts ────────────────────────────────────────────────────────────
    font_title    = pygame.font.SysFont("Consolas", 52, bold=True)
    font_subtitle = pygame.font.SysFont("Consolas", 18)
    font_btn_lg   = pygame.font.SysFont("Consolas", 28, bold=True)
    font_btn_sm   = pygame.font.SysFont("Consolas", 22, bold=True)
    font_hud      = pygame.font.SysFont("Consolas", 18)
    font_heading  = pygame.font.SysFont("Consolas", 36, bold=True)
    font_body     = pygame.font.SysFont("Consolas", 18)

    # ── Hand tracker ─────────────────────────────────────────────────────
    tracker = HandTracker(screen_width=SCREEN_W, screen_height=SCREEN_H)

    # ── Menu buttons ─────────────────────────────────────────────────────
    btn_start = UIButton(
        pygame.Rect(SCREEN_W // 2 - 160, SCREEN_H // 2 - 30, 320, 60),
        "START DUEL", font_btn_lg,
    )
    btn_deck = UIButton(
        pygame.Rect(SCREEN_W // 2 - 200, SCREEN_H // 2 + 70, 180, 50),
        "DECK", font_btn_sm,
    )
    btn_tutorial = UIButton(
        pygame.Rect(SCREEN_W // 2 + 20, SCREEN_H // 2 + 70, 180, 50),
        "TUTORIAL", font_btn_sm,
    )
    menu_buttons = [btn_start, btn_deck, btn_tutorial]

    # ── Sub-menu back button ─────────────────────────────────────────────
    btn_back = UIButton(
        pygame.Rect(30, 24, 120, 44),
        "← BACK", font_btn_sm,
    )

    # ── PLAYING state objects ────────────────────────────────────────────
    cards: list[Card] = build_hand(DECK_DATA)
    dragged_card: Card | None = None

    # ── State ────────────────────────────────────────────────────────────
    state = GameState.MENU
    running = True

    # Cursor state + rising-edge click tracker
    cursor_x: float = SCREEN_W / 2
    cursor_y: float = SCREEN_H / 2
    is_clicking: bool = False
    prev_clicking: bool = False          # for rising-edge detection

    # ── Game loop ────────────────────────────────────────────────────────
    while running:
        # ── Events ───────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state == GameState.MENU:
                    running = False
                else:
                    state = GameState.MENU

        # ── Gesture input (every state) ──────────────────────────────────
        prev_clicking = is_clicking
        cursor_x, cursor_y, is_clicking = tracker.get_cursor_state()
        click_rising = is_clicking and not prev_clicking   # new pinch this frame
        cx, cy = int(cursor_x), int(cursor_y)

        # ══════════════════════════════════════════════════════════════════
        #  STATE: MENU
        # ══════════════════════════════════════════════════════════════════
        if state == GameState.MENU:
            # Update hover states
            for btn in menu_buttons:
                btn.update_hover(cursor_x, cursor_y)

            # Rising-edge click detection on buttons
            if click_rising:
                if btn_start.hovered:
                    # Reset the playing field for a fresh duel
                    cards = build_hand(DECK_DATA)
                    dragged_card = None
                    state = GameState.PLAYING
                elif btn_deck.hovered:
                    state = GameState.DECK_SELECT
                elif btn_tutorial.hovered:
                    state = GameState.TUTORIAL

            # ── Draw MENU ────────────────────────────────────────────────
            screen.fill(COL_MENU_BG)

            # Decorative gradient bar at the top
            bar = pygame.Surface((SCREEN_W, 4), pygame.SRCALPHA)
            bar.fill((230, 200, 120, 180))
            screen.blit(bar, (0, 0))

            # Title
            title_surf = font_title.render("SOARING CARAKA", True, COL_TITLE)
            screen.blit(title_surf,
                        title_surf.get_rect(center=(SCREEN_W // 2,
                                                    SCREEN_H // 2 - 130)))
            # Subtitle
            sub_surf = font_subtitle.render(
                "A Gesture-Controlled Card Battler", True, COL_SUBTITLE)
            screen.blit(sub_surf,
                        sub_surf.get_rect(center=(SCREEN_W // 2,
                                                  SCREEN_H // 2 - 80)))
            # Buttons
            for btn in menu_buttons:
                btn.draw(screen)

            # Hint text at the bottom
            hint = font_subtitle.render(
                "Pinch to click  ·  Move your index finger to navigate",
                True, COL_SUBTITLE)
            screen.blit(hint,
                        hint.get_rect(center=(SCREEN_W // 2, SCREEN_H - 50)))

        # ══════════════════════════════════════════════════════════════════
        #  STATE: DECK SELECT
        # ══════════════════════════════════════════════════════════════════
        elif state == GameState.DECK_SELECT:
            btn_back.update_hover(cursor_x, cursor_y)
            if click_rising and btn_back.hovered:
                state = GameState.MENU

            # ── Draw DECK SELECT ─────────────────────────────────────────
            screen.fill(COL_MENU_BG)

            heading = font_heading.render("DECK BUILDER", True, COL_TITLE)
            screen.blit(heading,
                        heading.get_rect(center=(SCREEN_W // 2, 100)))

            # Show the current deck as a card fan
            fan_x = (SCREEN_W - len(DECK_DATA) * (CARD_W + 20)) // 2
            for i, data in enumerate(DECK_DATA):
                preview = Card(fan_x + i * (CARD_W + 20), 180, data)
                preview.draw(screen)

            placeholder = font_body.render(
                "Deck editing coming soon — your current deck is shown above.",
                True, COL_SUBTITLE)
            screen.blit(placeholder,
                        placeholder.get_rect(center=(SCREEN_W // 2,
                                                     SCREEN_H - 100)))
            btn_back.draw(screen)

        # ══════════════════════════════════════════════════════════════════
        #  STATE: TUTORIAL
        # ══════════════════════════════════════════════════════════════════
        elif state == GameState.TUTORIAL:
            btn_back.update_hover(cursor_x, cursor_y)
            if click_rising and btn_back.hovered:
                state = GameState.MENU

            # ── Draw TUTORIAL ────────────────────────────────────────────
            screen.fill(COL_MENU_BG)

            heading = font_heading.render("HOW TO PLAY", True, COL_TITLE)
            screen.blit(heading,
                        heading.get_rect(center=(SCREEN_W // 2, 80)))

            tutorial_lines = [
                "1.  Move your INDEX FINGER in front of the webcam to control the cursor.",
                "2.  PINCH your index finger and thumb together to CLICK / GRAB.",
                "3.  Drag cards from your HAND ZONE to the PLAY ZONE to play them.",
                "4.  If you drop a card outside the Play Zone, it snaps back to your hand.",
                "5.  Each card has a COST, ATK (attack), and HP (health).",
                "",
                "Good luck, Caraka!",
            ]
            for i, line in enumerate(tutorial_lines):
                line_surf = font_body.render(line, True, COL_BTN_TEXT)
                screen.blit(line_surf, (100, 160 + i * 40))

            btn_back.draw(screen)

        # ══════════════════════════════════════════════════════════════════
        #  STATE: PLAYING
        # ══════════════════════════════════════════════════════════════════
        elif state == GameState.PLAYING:
            if is_clicking:
                if dragged_card is not None:
                    # Continue dragging
                    dragged_card.x = cursor_x - dragged_card.width / 2
                    dragged_card.y = cursor_y - dragged_card.height / 2
                else:
                    # Try to grab the top-most card under the cursor
                    for card in reversed(cards):
                        if card.collidepoint(cursor_x, cursor_y):
                            card.is_dragging = True
                            dragged_card = card
                            card.x = cursor_x - card.width / 2
                            card.y = cursor_y - card.height / 2
                            break
            else:
                # ── Release / drop ───────────────────────────────────────
                if dragged_card is not None:
                    dragged_card.is_dragging = False
                    card_cx, card_cy = dragged_card.center

                    if PLAY_ZONE_RECT.collidepoint(card_cx, card_cy):
                        dragged_card.home_x = dragged_card.x
                        dragged_card.home_y = dragged_card.y
                    else:
                        dragged_card.snap_to_home()

                    cards.remove(dragged_card)
                    cards.append(dragged_card)
                    dragged_card = None

            # ── Draw PLAYING ─────────────────────────────────────────────
            screen.fill(COL_BG)

            # Zones
            draw_zone(screen, PLAY_ZONE_RECT,
                      COL_PLAY_ZONE, COL_PLAY_ZONE_BDR, "PLAY ZONE")
            draw_zone(screen, HAND_ZONE_RECT,
                      COL_HAND_ZONE, COL_HAND_ZONE_BDR, "HAND")

            # Cards
            for card in cards:
                card.draw(screen)

            # HUD
            click_lbl = "PINCH" if is_clicking else "OPEN"
            drag_lbl  = f"DRAGGING: {dragged_card.name}" if dragged_card \
                        else "IDLE"
            hud = font_hud.render(
                f"({cx}, {cy})  |  {click_lbl}  |  {drag_lbl}",
                True, COL_HUD_TEXT,
            )
            screen.blit(hud, (16, SCREEN_H - 36))

        # ══════════════════════════════════════════════════════════════════
        #  CURSOR — drawn LAST so it's always on top
        # ══════════════════════════════════════════════════════════════════
        draw_cursor(screen, cx, cy, is_clicking)

        pygame.display.flip()
        clock.tick(FPS)

    # ── Cleanup ──────────────────────────────────────────────────────────
    tracker.release()
    pygame.quit()
    sys.exit()


# ═════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
