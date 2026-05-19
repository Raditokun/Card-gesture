# Project Overview: Computer Vision Card Battler
This is a Python-based digital card game where the player uses their webcam to control the mouse via hand gestures to drag and drop cards onto a playing field.

**CORE RULE:** STRICTLY NO GAME ENGINES. Build from scratch using Pygame.

## 1. Tech Stack
* **Game Loop & UI:** Pygame
* **Computer Vision:** OpenCV + MediaPipe Hands (`mediapipe.solutions.hands`)
* **Assets:** Custom images for cards and UI

## 2. Architecture & Rules
* **Cursor Control:** The player's Index Finger Tip controls a virtual crosshair/cursor on the Pygame screen.
* **Click & Drag:** A "click" or "grab" is registered when the user performs a Pinch gesture (the distance between the Index Finger Tip and Thumb Tip falls below a certain threshold).
* **Coordinate Mapping:** The webcam coordinates must be mapped and scaled to the Pygame window resolution so the cursor reaches all corners of the screen.

## 3. File Structure
* `main.py`: Pygame initialization, game states, rendering the board, and the main loop.
* `gesture.py`: OpenCV webcam capture and MediaPipe Hands processing. Returns cursor (X, Y) and a boolean `is_clicking`.
* (Additional files like `cards.py` or `ui.py` will be added as we build out the game logic).

## 4. Agent Output Protocol
At the end of every response where code is written, provide a Markdown "Changelog Summary" detailing files created/modified and a brief explanation of the logic.