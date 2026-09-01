# sprites.py — Procedural pixel-art sprite generators using pygame.draw
"""
Every function returns a NEW Surface (48×48 by default, matching TILE_SIZE).
No external asset files are required.
"""

import pygame
from config import *


def _draw_frog_body(surf: pygame.Surface, cx: int, cy: int, scale: float = 1.0):
    """Draw a solid frog body (ellipse) in FROG_GREEN."""
    w = int(40 * scale)
    h = int(36 * scale)
    rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    pygame.draw.ellipse(surf, FROG_GREEN, rect)
    # darker outline
    pygame.draw.ellipse(surf, BLACK, rect, 2)


def _draw_frog_eyes(surf: pygame.Surface, cx: int, cy: int):
    """Draw two bulging eyes at the top of the frog."""
    eye_r = 5
    left = (cx - 10, cy - 14)
    right = (cx + 10, cy - 14)
    for ex, ey in (left, right):
        pygame.draw.circle(surf, WHITE, (ex, ey), eye_r)
        pygame.draw.circle(surf, BLACK, (ex, ey), eye_r, 1)
        # pupil
        pygame.draw.circle(surf, BLACK, (ex + 2, ey - 1), 2)


def _draw_frog_legs(surf: pygame.Surface, cx: int, cy: int):
    """Draw four legs extending outward."""
    for dx, dy in [(-22, 8), (-22, -4), (22, 8), (22, -4)]:
        pygame.draw.ellipse(surf, FROG_GREEN,
                            (cx + dx - 5, cy + dy - 3, 10, 6))


def frog_idle(cx: int = 24, cy: int = 24):
    """Return a fresh sprite Surface for the idle frog."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    _draw_frog_body(surf, cx, cy)
    _draw_frog_eyes(surf, cx, cy)
    _draw_frog_legs(surf, cx, cy)
    return surf


def frog_hop(cx: int = 24, cy: int = 24):
    """Return a sprite for the hopping animation (slightly larger)."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    _draw_frog_body(surf, cx, cy, scale=1.15)
    _draw_frog_eyes(surf, cx + 1, cy - 1)
    _draw_frog_legs(surf, cx, cy)
    return surf


def car_sprite(color: tuple = CAR_RED):
    """Return a top-down car sprite in the given colour."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    # body
    rect = pygame.Rect(8, 12, 32, 24)
    pygame.draw.rect(surf, color, rect, border_radius=6)
    pygame.draw.rect(surf, BLACK, rect, 2)
    # windshield
    if color == CAR_RED:
        ws = (14, 14, 20, 8)
    else:
        ws = (14, 26, 20, 8)
    pygame.draw.rect(surf, (150, 200, 255), ws, border_radius=2)
    return surf


def car_red():  return car_sprite(CAR_RED)
def car_blue(): return car_sprite(CAR_BLUE)
def car_yellow(): return car_sprite(CAR_YELLOW)
def car_green(): return car_sprite(CAR_GREEN)
def car_orange(): return car_sprite(CAR_ORANGE)


def log_brown(width: int = 36):
    """Return a horizontal log sprite."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    rect = pygame.Rect(24 - width // 2, 10, width, 28)
    pygame.draw.rect(surf, LOG_BROWN, rect, border_radius=10)
    pygame.draw.rect(surf, BLACK, rect, 2)
    return surf


def log_green_surf(width: int = 36):
    """Return a green-tinted log sprite."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    rect = pygame.Rect(24 - width // 2, 10, width, 28)
    pygame.draw.rect(surf, LOG_GREEN, rect, border_radius=10)
    pygame.draw.rect(surf, BLACK, rect, 2)
    return surf


def turtle_surf(count: int = 3):
    """Return a surface with *count* stacked turtle sprites."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    spacing = TILE_SIZE // (count + 1)
    for i in range(count):
        tx = 24 - spacing // 2 + i * spacing
        ty = 24
        pygame.draw.circle(surf, TURTLE_GREEN, (tx, ty), 8)
        pygame.draw.circle(surf, BLACK, (tx, ty), 8, 1)
    return surf


def rock_surf():
    """Return a single safe 'rock' for the river island."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    rect = pygame.Rect(6, 6, 36, 36)
    pygame.draw.rect(surf, (105, 105, 105), rect, border_radius=8)
    pygame.draw.rect(surf, BLACK, rect, 2)
    return surf


def home_slot_sprite(active: bool = False):
    """Return the background for a home slot."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    color = HOME_ACTIVE if active else HOME_BG
    pygame.draw.rect(surf, color, surf.get_rect())
    return surf


def spawn_marker():
    """Mark where the frog spawns at the bottom."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(surf, (200, 200, 200), (24, 24), 18, 3)
    return surf
