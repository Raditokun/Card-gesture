import cv2
import math
import mediapipe as mp


class HandTracker:
    """
    Uses OpenCV + MediaPipe Hands to track the player's index finger
    as a virtual cursor and detect a pinch gesture as a click/grab.

    Usage:
        tracker = HandTracker(screen_width=1280, screen_height=720)
        # In your game loop:
        cx, cy, clicking = tracker.get_cursor_state()
        # When done:
        tracker.release()
    """

    # MediaPipe Hands landmark indices
    INDEX_FINGER_TIP = 8
    THUMB_TIP = 4

    def __init__(
        self,
        screen_width: int = 1280,
        screen_height: int = 720,
        smoothing: float = 0.3,
        pinch_threshold: float = 0.05,
    ):
        """
        Parameters
        ----------
        screen_width : int
            The width of the Pygame window to map coordinates to.
        screen_height : int
            The height of the Pygame window to map coordinates to.
        smoothing : float
            Exponential moving average factor (0–1). Lower = smoother
            but laggier; higher = more responsive but jittery.
            0.3 is a solid default for 30 fps webcam input.
        pinch_threshold : float
            Maximum normalised distance between the index finger tip
            and thumb tip to register as a "pinch" / click.  Since
            MediaPipe landmarks are normalised 0-1, 0.05 ≈ 5 % of the
            frame diagonal — a tight pinch.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.smoothing = smoothing
        self.pinch_threshold = pinch_threshold

        # ── OpenCV webcam ────────────────────────────────────────────────
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("[HandTracker] ERROR: Could not open webcam.")

        # ── MediaPipe Hands ──────────────────────────────────────────────
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
        )

        # ── Smoothed cursor state ────────────────────────────────────────
        self._smooth_x: float = screen_width / 2
        self._smooth_y: float = screen_height / 2

    # ─── Public API ─────────────────────────────────────────────────────────

    def get_cursor_state(self) -> tuple[float, float, bool]:
        """
        Read one webcam frame, run hand detection, and return the
        smoothed cursor position + click state.

        Returns
        -------
        (cursor_x, cursor_y, is_clicking)
            cursor_x / cursor_y : float
                Smoothed screen-space coordinates of the index finger tip.
            is_clicking : bool
                True when the index finger tip and thumb tip are pinched
                together (distance < pinch_threshold).
        """
        success, frame = self.cap.read()
        if not success:
            # Return last known position, not clicking
            return self._smooth_x, self._smooth_y, False

        # Mirror the frame so the cursor moves in the expected direction
        frame = cv2.flip(frame, 1)

        # Convert BGR → RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False          # small perf hint for MediaPipe
        results = self.hands.process(rgb)

        if not results.multi_hand_landmarks:
            # No hand detected — keep the last smoothed position, not clicking
            return self._smooth_x, self._smooth_y, False

        # Use the first (and only) detected hand
        hand_landmarks = results.multi_hand_landmarks[0]

        index_tip = hand_landmarks.landmark[self.INDEX_FINGER_TIP]
        thumb_tip = hand_landmarks.landmark[self.THUMB_TIP]

        # ── Map normalised coords (0-1) to screen pixels ────────────────
        raw_x = index_tip.x * self.screen_width
        raw_y = index_tip.y * self.screen_height

        # ── Exponential moving average smoothing ────────────────────────
        self._smooth_x += self.smoothing * (raw_x - self._smooth_x)
        self._smooth_y += self.smoothing * (raw_y - self._smooth_y)

        # ── Pinch detection ─────────────────────────────────────────────
        distance = math.hypot(
            index_tip.x - thumb_tip.x,
            index_tip.y - thumb_tip.y,
        )
        is_clicking = distance < self.pinch_threshold

        return self._smooth_x, self._smooth_y, is_clicking

    def release(self) -> None:
        """Release the webcam and close MediaPipe resources."""
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        if self.hands is not None:
            self.hands.close()
        print("[HandTracker] Camera released. MediaPipe closed.")