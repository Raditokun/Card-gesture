from __future__ import annotations
from typing import Optional, List
from enum import Enum
import pyglet
import inspect

# Init Functions
_window: Optional[pyglet.window.BaseWindow] = None
_fps : int = 60
def InitPyglem(width = 1280, height = 720, fps = 60, title = "Pyglem Window", fullscreen = False):
    global _window, _fps
    _fps = fps
    _window = pyglet.window.Window(width, height, title, fullscreen=fullscreen)

# Pools
SpritePool: List[pyglet.sprite.Sprite] = []

# Enums
class AnchorX(Enum):
    Left = 0,
    Center = 1,
    Right = 2,

class AnchorY(Enum):
    Top = 0,
    Center = 1,
    Bottom = 2,

# Helper
def ScreenWidth():
    try:
        return _window.width
    except:
        return 0

def ScreenHeight():
    try:
        return _window.height
    except:
        return 0

# Classes
class Sprite:
    _sprite_image: Optional[pyglet.image.AbstractImage] = None
    _sprite: Optional[pyglet.sprite.Sprite] = None

    def __init__(self) -> None:
        pass

    def Load(self, sprite_path, anchorx: AnchorX = None, anchory: AnchorY = None) -> None:
        if not sprite_path:
            print("Warning: No Sprite Path Given")
            return
        
        self._sprite_image = pyglet.image.load(sprite_path)
        
        if anchorx == AnchorX.Left: self._sprite_image.anchor_x = 0
        elif anchorx == AnchorX.Center: self._sprite_image.anchor_x = self._sprite_image.width // 2
        elif anchorx == AnchorX.Right: self._sprite_image.anchor_x = self._sprite_image.width

        if anchory == AnchorY.Top: self._sprite_image.anchor_y = self._sprite_image.height
        elif anchory == AnchorY.Center: self._sprite_image.anchor_y = self._sprite_image.height // 2
        elif anchory == AnchorY.Bottom: self._sprite_image.anchor_y = 0

        self._sprite = pyglet.sprite.Sprite(self._sprite_image)
    
    def Draw(self) -> None:
        global SpritePool

        if self._sprite is not None:
            SpritePool.append(self._sprite)
        else:
            print("Warning: Cannot draw, sprite not loaded yet!")

    def UnDraw(self) -> None:
        global SpritePool

        if self._sprite is not None:
            try:
                SpritePool.remove(self._sprite)
            except ValueError:
                print("Error: Cannot Undraw, sprite not available in pool")
        else:
            print("Warning: Cannot draw, sprite not loaded yet!")


    # --- X Coordinate Property ---
    @property
    def x(self) -> float:
        """Gets the X position of the sprite."""
        if self._sprite:
            return self._sprite.x
        return 0.0

    @x.setter
    def x(self, value: float) -> None:
        """Sets the X position of the sprite."""
        if self._sprite:
            self._sprite.x = value
        else:
            print("Warning: Cannot set X, sprite not loaded yet!")

    # --- Y Coordinate Property ---
    @property
    def y(self) -> float:
        """Gets the Y position of the sprite."""
        if self._sprite:
            return self._sprite.y
        return 0.0

    @y.setter
    def y(self, value: float) -> None:
        """Sets the Y position of the sprite."""
        if self._sprite:
            self._sprite.y = value
        else:
            print("Warning: Cannot set Y, sprite not loaded yet!")

    # --- Scale Property ---
    @property
    def scale(self) -> float:
        """Gets the scale of the sprite."""
        if self._sprite:
            return self._sprite.scale
        return 0.0

    @scale.setter
    def scale(self, value: float) -> None:
        """Sets the scale of the sprite."""
        if self._sprite:
            self._sprite.scale = value
        else:
            print("Warning: Cannot set scale, sprite not loaded yet!")
            
    # --- Scale Property ---
    @property
    def rotation(self) -> float:
        """Gets the rotation of the sprite."""
        if self._sprite:
            return self._sprite.rotation
        return 0.0

    @rotation.setter
    def rotation(self, value: float) -> None:
        """Sets the rotation of the sprite."""
        if self._sprite:
            self._sprite.rotation = value
        else:
            print("Warning: Cannot set rotation, sprite not loaded yet!")


# Window Events
_user_update_func : Optional[function] = None

def _internal_update(dt):
    if _user_update_func:
        sig = inspect.signature(_user_update_func)
        
        if len(sig.parameters) > 0:
            _user_update_func(dt)
        else:
            _user_update_func()

def on_draw():
    if _window:
        _window.clear()
    for sprite in SpritePool:
        sprite.draw()

def OnUpdate(func : function):
    global _user_update_func
    _user_update_func = func
    return func

def Run() -> None:
    global _window
    if _window:
        _window.push_handlers(on_draw)
        pyglet.clock.schedule_interval(_internal_update, 1/_fps)
        pyglet.app.run()
    else:
        print("Window Must Be Initiated before calling Run()")