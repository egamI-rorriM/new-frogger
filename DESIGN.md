# Frogger - Game Design Document (GDD)

## 1. Overview
- **Genre**: Classic Arcade / Puzzle
- **Visual Style**: Pixel Art (48×48px tiles)
- **Canvas Size**: 720×672 pixels (15 tiles wide × 14 tiles tall)
- **Engine**: Pygame (Python)
- **Target Resolution**: 960×896 (scale by 1.33x for desktop, keep per-tile at 48px)
- **Game Loop**: Single endless screen with increasing difficulty

---

## 2. Board Layout (15 × 14 grid)

```
Row 0:  [HOME] . . [HOME] . [HOME] . [HOME] . [HOME]     ← Goal slots (water, safe rock base)
Row 1-2:  [Grass Buffer Zone]
Row 3:    [Log Lane 1] - Logs moving right                     ← Transport frog
Row 4:    [Turtle Lane 2] - Pairs of turtles moving left       ← Transport frog
Row 5:    [Rock Island] - Stationary safe zone (partial width)   ← Must ride to cross
Row 6:    [Turtle Lane 3] - Triple turtles moving right        ← Transport frog
Row 7-8:  [River End Buffer Zone]
Row 9:     [Median Strip]
Row 10:   [Fast Car Lane] - Cars moving left                     ← Fast!
Row 11:   [Truck Lane 1] - Trucks moving right
Row 12:   [Small Car Lane] - Sedans moving left
Row 13:   [Spawn Lane / Start Zone]
```

**Key**: Each tile = 48×48 pixels. Road/river lanes are 1 row each. Safe zones (grass, median) separate lanes.

---

## 3. Frog

### Appearance
- Classic green frog sprite (pixel art)
- 4 frames hopping animation (right-facing)
- 4 frames hopping animation (left-facing, mirror of right)
- Death animation (flip/expand then shrink)
- Sprite size: 48×48 pixels

### Behavior
- **Movement**: Grid-hop — press UP/DOWN/LEFT/RIGHT to move one tile at a time
- **Transport**: When on a log or turtle pair, frog moves WITH that platform's speed
- **Death conditions**:
  - Car hits the frog (collision with any vehicle)
  - Frog touches water WITHOUT riding a platform (drowns)
  - Frog is between two home slots (falls in gap) — this is actually already handled by water collision
- **Respawn**: Returns to spawn position after death, loses one life
- **Victory condition for row**: Must reach any of the 5 HOME slots on Row 0

### Starting Position
- Center of Row 13: tile (7, 13) = pixel (336, 624) — center bottom screen

---

## 4. Vehicles / Obstacles

### Road Lanes (Rows 10, 11, 12)
| Lane | Vehicle Type | Direction | Base Speed | Sprite Dimensions | Color Palette |
|------|-------------|-----------|------------|-------------------|---------------|
| Row 12 | Small Car (Sedan) | Left | 80 px/s | 64×32 | Red/Silver |
| Row 11 | Truck | Right | 120 px/s | 80×32 | Yellow/Black |
| Row 10 | Fast Car (Sports) | Left | 160 px/s | 56×32 | Blue/Chrome |

- **Spacing**: Cars/trucks spawn at random intervals — no fixed distance, just random gaps
- **Collision**: Vehicle sprite colliding with frog sprite = death
- **Sprite**: Pixel art car, each type distinct visual

### River Lanes (Rows 3, 4, 5, 6, 7)
| Lane | Platform Type | Direction | Base Speed | Dimensions | Notes |
|------|-------------|-----------|------------|------------|-------|
| Row 8 | Log | Right | 100 px/s | ~96×32 px (3 tile width) | Single log, wide platform |
| Row 7 | Turtle Pair | Left | 70 px/s | ~48×32 px (two turtles) | Two stacked turtles = one platform |
| Row 6 | Rock Island | Stationary | 0 px/s | ~96×48 px (2-3 tiles wide) | Always there, no movement |
| Row 5 | Turtle Triple | Right | 100 px/s | ~72×32 px (three turtles) | Three stacked turtles |
| Row 4 | Log | Left | 80 px/s | ~96×32 px (3 tile width) | Single log, narrower look |

### Platform Rules
- Platforms spawn with random X offset on each loop
- When a platform exits the screen, it respawns at the opposite side after a delay
- **Carrying frog**: Frog rides the top of the platform automatically (position follows platform's movement)
- The player still controls frog direction while riding — they can jump onto another platform mid-transit

---

## 5. Home Slots (Row 0)

### Appearance
- Five "holes" cut into the water banks at positions: tile (1,0), (3,0), (5,0), (7,0), (9,0)
- Each slot is one tile wide (48×48 pixels)
- Water background in each slot (animated waves)
- Rock base under each slot (green/brown pixel art)

### Behavior
- **Frog enters a slot**: If frog sprite fully fits inside a slot → "HOME!" score awarded
- **Slot fills up**: Once filled, it stays filled for the rest of that round (visual: frog sits in slot)
- **All 5 slots filled**: Wave complete — bonus points!
- **Frog cannot exit**: Once a frog is in a home slot, it can't move out (it's "home")

---

## 6. Scoring System

### Per-Ride Points
| Action | Points | Notes |
|--------|--------|-------|
| Cross road lane | +25 pts | Each road lane crossed safely (once per lane, not per frame) |
| Cross river lane | +50 pts | Each river lane crossed safely while riding a platform (once per lane) |
| Reach home slot | +100 pts | One time per slot filled |

### Wave Bonus
- When all 5 home slots are filled: **Bonus = 500 × wave number**
- Example: Wave 3 bonus = 1,500 points

### Speed Multiplier
- Each vehicle has a "speed multiplier" based on current wave (see difficulty below)
- Displayed as a small HUD element during gameplay

---

## 7. Difficulty / Waves

| Metric | Details |
|--------|---------|
| **Wave progression** | When all 5 home slots are filled, next wave begins |
| **Speed increase** | Vehicle/platform speeds multiply by **1.08 per wave** (capped at 2× base speed) |
| **Spawn frequency** | Vehicles spawn slightly faster each wave (+5% chance per lane per wave) |
| **Starting speed** | Wave 1 = base speeds listed in tables above |

---

## 8. Lives & Game Over

- **Lives**: 5 per game (displayed as small frog icons top-right corner)
- **On death**: Frog returns to spawn position, screen flashes red briefly, lose one life
- **Game over**: When all 5 lives are lost → Show "GAME OVER" with final score
- **Restart**: Press ENTER or SPACE to restart game

---

## 9. UI / HUD Elements

### Top Bar (Row -1 area, ~48px height above main board)
| Element | Position | Display |
|---------|----------|---------|
| Score | Left side | "SCORE: XXXXXX" in white pixel font |
| Wave | Center-left | "WAVE X" (X = current wave number) |
| High Score | Center-right | "HI: HHHHHH" |
| Lives | Right side | Small frog icons (1 per remaining life) |

### Bottom Bar (optional, above spawn area)
| Element | Position | Display |
|---------|----------|---------|
| Speed indicator | Below board | Shows current speed multiplier "SPEED: 1.0x" |

### Screens
- **Title Screen**: Game title in pixel art, "PRESS SPACE TO START", animated frog sprite, start music playing
- **Game Over**: "GAME OVER" text, final score, high score, "PRESS ENTER TO RESTART"
- **Home Slot Filled**: Brief "+100!" popup at the slot location (flashes for 1 second)

---

## 10. Audio

### Sound Effects (generated via ComfyUI Stable Diffusion / audio tools)
| Event | Description |
|-------|-------------|
| Hop | Short "boing" sound (frog jumps) |
| Home | Cheerful ding/dong (frog reaches home) |
| Die | Descending tonal sweep (frog dies) |
| Wave Complete | Upward arpeggio fanfare (wave completed) |
| Game Over | Somber descending chord |
| Car Pass (near miss) | Low rumble (when car passes within 1 tile) |

### Music
- **Style**: Chiptune, upbeat, retro arcade feel
- **Duration**: ~60 second loop
- **Mood**: Energetic but not too intense — classic Frogger vibe
- **Generation Tool**: ACE-Step via ComfyUI (generate_music tool)

---

## 11. File Structure

```
new-frogger/
├── DESIGN.md              # This document
├── config.py              # All constants (tile sizes, colors, speeds, scoring)
├── main.py                # Entry point: pygame init, window, game loop
├── assets/
│   ├── sprites/           # Pixel art PNG files
│   │   ├── frog_right_1.png  (and _2, _3, _4 — hop frames)
│   │   ├── frog_left_1.png
│   │   ├── frog_dead.png
│   │   ├── car_red_sedan.png
│   │   ├── truck_yellow.png
│   │   ├── car_blue_fast.png
│   │   ├── log.png
│   │   ├── turtle_pair.png
│   │   ├── turtle_triple.png
│   │   ├── rock_island.png
│   │   └── home_slot.png
│   ├── backgrounds/
│   │   ├── road_bg.png    # Asphalt texture for road lanes
│   │   ├── river_bg.png   # Water wave texture for river lanes
│   │   └── grass_bg.png   # Grass texture for buffer zones
│   └── audio/
│       ├── hop.wav
│       ├── home.wav
│       ├── die.wav
│       ├── wave_complete.wav
│       ├── game_over.wav
│       └── car_pass.wav
│       └── music_loop.wav
├── game_state.py          # Core game logic: classes for Frog, Vehicle, Platform, GameState
├── sprite_loader.py       # Loads PNGs into pygame surfaces, handles animations
├── ui.py                  # HUD drawing, screen rendering (title, game over)
└── requirements.txt       # Python dependencies (pygame only)
```

---

## 12. Implementation Phases (for reference during coding)

| Phase | What | Priority |
|-------|------|----------|
| P0 - Config & Setup | `config.py`, `main.py` window init, requirements.txt | 🔴 MVP |
| P1 - Core Game | `game_state.py`: frog, vehicles, platforms, collision, scoring | 🔴 MVP |
| P2 - Rendering | `sprite_loader.py`, basic drawing to screen | 🔴 MVP |
| P3 - UI/HUD | `ui.py`: score display, lives, title/game-over screens | 🟡 Important |
| P4 - Audio | Sound effects + background music | 🟡 Nice-to-have |
| P5 - Polish | Animations, particle effects, screen shake on death | 🟢 Future |

---

## 13. MVP Acceptance Criteria

- [ ] Game window opens with pygame (720×672 canvas)
- [ ] Grid-based frog can move UP/DOWN/LEFT/RIGHT with arrow keys
- [ ] Frog starts at spawn position on Row 13
- [ ] Road vehicles scroll continuously across their lanes, respawn when off-screen
- [ ] River platforms scroll, frog carries correctly while standing on them
- [ ] Frog dies if hit by vehicle or touches water without platform
- [ ] Frog reaches home slot → score increases, slot fills permanently
- [ ] Wave completes when all 5 slots filled → bonus points, next wave with faster speeds
- [ ] Lives decrease on death, game over at 0 lives
- [ ] Score and lives displayed in HUD
- [ ] Title screen and Game Over screen work
- [ ] Sprite sheets generated (pixel art placeholders)
- [ ] Audio assets generated (placeholder sounds + music loop)
