# config.py — Constants and configuration for Frogger

import pygame

# ── Display ──────────────────────────────────────────────────────────────────
TILE_SIZE = 48          # pixels per grid cell
COLS, ROWS = 15, 13    # board dimensions (columns × rows)
CANVAS_WIDTH = COLS * TILE_SIZE   # 720 px
CANVAS_HEIGHT = ROWS * TILE_SIZE  # 624 px
FPS = 60

# ── Colours (R, G, B) ────────────────────────────────────────────────────────
BG_ROAD     = (50,  50,  50)
BG_GRASS    = (34, 139,  34)
BG_WATER    = (30, 144, 255)
FROG_GREEN  = (50, 205,  50)
CAR_RED     = (220,  20,  60)
CAR_BLUE    = (30, 144, 255)
CAR_YELLOW  = (255, 215,   0)
CAR_GREEN   = (34, 139,  34)
CAR_ORANGE  = (255, 165,   0)
LOG_BROWN   = (139,  69,  19)
LOG_GREEN   = (34, 100,  34)
TURTLE_GREEN= (0,   128,  0)
HOME_BG     = (34, 139,  34)    # grass inside home slots
HOME_ACTIVE = (150, 255, 150)    # lit-up slot colour
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
HUD_BG      = (0,   0,   0)

# ── Board rows (top=0 → bottom=ROWS-1) ───────────────────────────────────────
# Row layout:
#   0 : HOME row  (5 goal slots, 5 gaps)
#   1-2 : upper grass buffer
#   3-8 : RIVER lanes  (logs / turtles float right or left)
#   9   : lower grass median
#   10-11: ROAD lanes (cars drive left or right)
#   12 : SPAWN row

HOME_ROW = 0
RIVER_START, RIVER_END = 3, 8       # inclusive
ROAD_START, ROAD_END = 10, 11       # inclusive
SPAWN_ROW = 12

# ── Lane definitions (row → list of dicts) ───────────────────────────────────
# direction: -1 = left, +1 = right
# speed   : cells per second (base value; multiplied by wave_scale later)

ROAD_LANES = [
    {"row": 10, "direction": -1, "speed": 2.0, "vehicles": ["car_red"],    "interval": 80},
    {"row": 11, "direction": +1, "speed": 2.5, "vehicles": ["car_blue"],   "interval": 70}, # Fixed: Row 9 is grass! This should be row 11 to match the board layout.
]

RIVER_LANES = [
    {"row": 3,  "speed": 1.2, "objects": ["log"],         "interval": 60, "dir": +1},
    {"row": 4,  "speed": 1.5, "objects": ["log_green"],   "interval": 55, "dir": -1},
    {"row": 5,  "speed": 1.8, "objects": ["turtle"],      "interval": 50, "dir": +1},
    {"row": 6,  "speed": 2.0, "objects": ["log"],         "interval": 45, "dir": -1},
    {"row": 7,  "speed": 2.3, "objects": ["log_green"],   "interval": 40, "dir": +1},
    {"row": 8,  "speed": 1.6, "objects": ["log", "turtle"], "interval": 50, "dir": -1}, # Added row 8 so you don't fall through the bottom gap!
]

# ── Home slots (columns that accept the frog) ────────────────────────────────
HOME_SLOTS = [2, 5, 8, 11, 14]          # column indices in row HOME_ROW
HOME_SLOT_COUNT = len(HOME_SLOTS)

# ── Scoring ──────────────────────────────────────────────────────────────────
SCORE_PER_ROAD_LANE = 25
SCORE_PER_RIVER_LANE = 50
SCORE_HOME = 100
WAVE_BONUS = 500
LIVES_MAX = 5
WIN_WAVE = 10

# ── Difficulty scaling ───────────────────────────────────────────────────────
WAVE_SPEED_MULT = 0.08      # 8% faster per wave (cap at 2×)
FROG_MOVE_SPEED = TILE_SIZE * 4   # px/sec for grid-hopping animation

# ── Game states ──────────────────────────────────────────────────────────────
STATE_START = "start"
STATE_PLAYING = "playing"
STATE_DYING = "dying"       # brief death animation / invulnerability
STATE_WIN = "win"
STATE_GAMEOVER = "gameover"
STATE_PAUSED = "paused"
STATE_WAVE_TRANSITION = "wave_transition"

# ── Transition timing ────────────────────────────────────────────────────────
WAVE_TRANSITION_TIME = 1.5  # seconds to show wave complete screen
