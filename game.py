# game.py — Core game logic (lanes, entities, collisions, scoring)

import pygame
import random
from config import *
from sprites import (
    frog_idle, frog_hop,
    car_red, car_blue, car_yellow, car_green, car_orange,
    log_brown, log_green_surf, turtle_surf, rock_surf,
)


class Frog:
    """Player-controlled frog with grid-hop movement."""

    def __init__(self):
        self.reset()
        self.target_col = self.col
        self.target_row = self.row
        self.progress = 0.0          # 0→1 for hop animation
        self.moving = False
        self.on_wood = None           # Log/Turtle currently riding

    def reset(self):
        self.col = 7                 # spawn in the middle column
        self.row = SPAWN_ROW
        self.x = self.col * TILE_SIZE + (TILE_SIZE // 2)
        self.y = self.row * TILE_SIZE + (TILE_SIZE // 2)
        self.target_col = self.col
        self.target_row = self.row
        self.progress = 1.0          # start fully placed
        self.moving = False
        self.on_wood = None
        self.in_home = [False] * HOME_SLOT_COUNT

    def move(self, dc: int, dr: int) -> bool:
        """Attempt a hop by (dc, dr). Returns True if valid."""
        nc = self.target_col + dc
        nr = self.target_row + dr
        # stay inside the board columns
        if nc < 0 or nc >= COLS:
            return False
        # cannot enter home gaps — check slot membership
        if nr == HOME_ROW:
            in_slot = nc in HOME_SLOTS
            if not in_slot:
                return False
        self.target_col, self.target_row = nc, nr
        self.progress = 0.0
        self.moving = True
        return True

    def update(self, dt: float):
        """Advance hop animation. Call every frame."""
        if self.moving and self.progress < 1.0:
            self.progress += (FROG_MOVE_SPEED / TILE_SIZE) * dt
            if self.progress >= 1.0:
                self.col = self.target_col
                self.row = self.target_row
                self.progress = 1.0
                self.moving = False
        # lerp between source and target
        src_x = self.col * TILE_SIZE + (TILE_SIZE // 2)
        src_y = self.row * TILE_SIZE + (TILE_SIZE // 2)
        dst_x = self.target_col * TILE_SIZE + (TILE_SIZE // 2)
        dst_y = self.target_row * TILE_SIZE + (TILE_SIZE // 2)
        self.x = src_x + (dst_x - src_x) * min(self.progress, 1.0)
        self.y = src_y + (dst_y - src_y) * min(self.progress, 1.0)

    def at_home_slot(self):
        """Return index of home slot landed in, or None."""
        if self.target_row == HOME_ROW and not self.moving:
            idx = HOME_SLOTS.index(self.target_col)
            return idx
        return None

    def is_riding(self):
        """Is the frog currently on a floating object?"""
        return self.on_wood is not None


class Vehicle(pygame.sprite.Sprite):
    """A road vehicle."""

    _sprite_cache = {}  # colour → sprite surface, shared across instances

    def __init__(self, row: int, x: float, direction: int, colour_fn):
        super().__init__()
        self.colour_fn = colour_fn
        self.image = self._get_sprite(colour_fn)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = row * TILE_SIZE + (TILE_SIZE // 2)
        self.row = row
        self.direction = direction   # -1 or +1
        self.speed = 0.0             # set by Game

    def _get_sprite(self, colour_fn):
        key = colour_fn.__name__
        if key not in Vehicle._sprite_cache:
            Vehicle._sprite_cache[key] = colour_fn()
        return Vehicle._sprite_cache[key].copy()

    def update(self, dt: float):
        self.rect.x += self.speed * self.direction * dt


class FloatingEntity(pygame.sprite.Sprite):
    """A log or turtle platform on the river."""

    _sprite_cache = {}  # (type_name, width) → sprite surface

    def __init__(self, row: int, x: float, width: int, direction: int,
                 obj_type: str, sprite_fn):
        super().__init__()
        key = (obj_type, width)
        if key not in FloatingEntity._sprite_cache:
            FloatingEntity._sprite_cache[key] = sprite_fn(width)
        self.image = FloatingEntity._sprite_cache[key].copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = row * TILE_SIZE + (TILE_SIZE // 2)
        self.row = row
        self.direction = direction
        self.speed = 0.0

    def update(self, dt: float):
        self.rect.x += self.speed * self.direction * dt


class Rock(pygame.sprite.Sprite):
    """A stationary rock in the river (safe spot)."""

    def __init__(self, row: int, x: float):
        super().__init__()
        self.image = rock_surf()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = row * TILE_SIZE + (TILE_SIZE // 2)
        self.row = row

    def update(self, dt: float):
        pass  # stationary


class Game:
    """Manages the full Frogger game state."""

    def __init__(self, sounds=None):
        self.sounds = sounds or {}
        self.state = STATE_START
        self.score = 0
        self.lives = LIVES_MAX
        self.wave = 1
        self.home_fills = [False] * HOME_SLOT_COUNT
        self.frog = Frog()
        self.cars = pygame.sprite.Group()
        self.logs = pygame.sprite.Group()
        self.rock_group = pygame.sprite.Group()
        self.last_car_spawn = {}    # row → last frame count
        self.last_wood_spawn = {}   # row → last frame count
        self.wave_scale = 1.0
        self.death_timer = 0.0      # frames remaining for death animation
        self.in_water_grace = 0.0   # grace period before water kills you
        self.wave_transition_timer = 0.0
        self.paused = False
        self.reset_wave()

    def play_sound(self, sound_name: str):
        """Play a named sound effect."""
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

    def reset_wave(self):
        """Reset wave-specific counters."""
        self.wave_scale = min(2.0, 1.0 + (self.wave - 1) * WAVE_SPEED_MULT)
        self.cars.empty()
        self.logs.empty()
        self.last_car_spawn = {}    # Reset spawn timers for new wave
        self.last_wood_spawn = {}   # Reset spawn timers for new wave
        # spawn initial cars
        # Map vehicle names to their sprite generators
        _VEHICLE_SPRITES = {
            "car_red": car_red, "car_blue": car_blue, "car_yellow": car_yellow,
            "car_green": car_green, "car_orange": car_orange,
        }

        for lane in ROAD_LANES:
            direction = lane["direction"]
            vehicle_name = lane["vehicles"][0]
            colour_fn = _VEHICLE_SPRITES.get(vehicle_name, car_red)
            for col in range(-1, COLS + 2):
                if random.random() < 0.5:  # ~50% chance per car slot
                    x = col * TILE_SIZE + (TILE_SIZE // 2)
                    v = Vehicle(lane["row"], x, direction, colour_fn)
                    v.speed = lane["speed"] * self.wave_scale * TILE_SIZE
                    self.cars.add(v)

        # spawn initial logs
        for lane in RIVER_LANES:
            sprite_map = {"log": log_brown, "log_green": log_green_surf,
                          "turtle": turtle_surf}
            obj_type = random.choice(lane["objects"])
            width = 36 if obj_type == "log" else 40
            fn = sprite_map.get(obj_type, log_brown)
            for col in range(-1, COLS + 2):
                if random.random() < 0.5:
                    x = col * TILE_SIZE + (TILE_SIZE // 2)
                    flo = FloatingEntity(lane["row"], x, width, lane["dir"],
                                         obj_type, fn)
                    flo.speed = lane["speed"] * self.wave_scale * TILE_SIZE
                    self.logs.add(flo)

        # rocks on river (safe island in the middle of the river)
        ISLAND_ROWS = [4, 5, 6]   # spans across these river lanes
        for row in ISLAND_ROWS:
            for col_offset in range(-1, 3):  # 3 tiles wide, centered around col 7
                rock = Rock(row, (7 + col_offset) * TILE_SIZE + (TILE_SIZE // 2))
                self.rock_group.add(rock)

    def start_game(self):
        """Start a new game."""
        self.score = 0
        self.lives = LIVES_MAX
        self.wave = 1
        self.home_fills = [False] * HOME_SLOT_COUNT
        self.frog.reset()
        self.state = STATE_PLAYING
        self.reset_wave()

    def respawn(self):
        """Frog lost a life — reset to spawn."""
        self.lives -= 1
        self.frog.reset()
        self.home_fills = [False] * HOME_SLOT_COUNT
        if self.lives <= 0:
            self.state = STATE_GAMEOVER
        else:
            # brief invulnerability / death animation handled in main loop
            pass
        self.play_sound("sfx_death")

    def frog_reaches_home(self):
        """Handle frog landing in a home slot."""
        idx = self.frog.at_home_slot()
        if idx is not None and not self.home_fills[idx]:
            self.home_fills[idx] = True
            self.score += SCORE_HOME
            self.play_sound("sfx_ding")
            self.frog.reset()
            if all(self.home_fills):
                self.wave += 1
                if self.wave > WIN_WAVE:
                    self.state = STATE_WIN
                else:
                    self.score += WAVE_BONUS
                    # Trigger wave transition screen
                    self.state = STATE_WAVE_TRANSITION
                    self.wave_transition_timer = WAVE_TRANSITION_TIME

    def check_wood_riding(self):
        """Update frog's wood-riding state."""
        self.frog.on_wood = None
        # Use rect intersection for reliable grid-hop sticking (fixes falling)
        frog_rect = pygame.Rect(int(self.frog.x - 12), int(self.frog.y - 12), 24, 24)
        for log in self.logs:
            # inflate log hitbox for forgiving riding
            log_hit = log.rect.inflate(8, 8)
            if frog_rect.colliderect(log_hit):
                self.frog.on_wood = log
                break

    def check_death_water(self):
        """Check if frog is in water without floating on anything."""
        if RIVER_START <= self.frog.row <= RIVER_END:
            if not self.frog.is_riding():
                return True
        return False

    def update(self, dt: float):
        """Update all game logic every frame."""
        if self.state == STATE_WAVE_TRANSITION:
            self.wave_transition_timer -= dt
            if self.wave_transition_timer <= 0:
                self.reset_wave()
                self.home_fills = [False] * HOME_SLOT_COUNT
                self.state = STATE_PLAYING
            return

        if self.state == STATE_PAUSED or self.state != STATE_PLAYING:
            return

        # update frog animation
        self.frog.update(dt)

        # update cars
        for car in self.cars:
            car.update(dt)
        # remove off-screen cars
        for car in self.cars.sprites():
            if (car.direction == -1 and car.rect.right < 0) or \
               (car.direction == +1 and car.rect.left > CANVAS_WIDTH):
                car.kill()

        # Continuous spawning of cars from the correct edge
        _VEHICLE_SPRITES = {
            "car_red": car_red, "car_blue": car_blue, "car_yellow": car_yellow,
            "car_green": car_green, "car_orange": car_orange,
        }
        for lane in ROAD_LANES:
            row = lane["row"]
            dirn = lane["direction"]
            vehicle_name = lane["vehicles"][0]
            colour_fn = _VEHICLE_SPRITES.get(vehicle_name, car_red)

            if row not in self.last_car_spawn:
                self.last_car_spawn[row] = 0

            self.last_car_spawn[row] += 1
            interval_s = lane.get("interval", 80)

            if self.last_car_spawn[row] >= interval_s:
                self.last_car_spawn[row] = 0

                # Spawn just outside the screen edge OPPOSITE to movement direction
                spawn_x = -TILE_SIZE // 2 if dirn == 1 else CANVAS_WIDTH + TILE_SIZE // 2

                v = Vehicle(lane["row"], spawn_x, dirn, colour_fn)
                v.speed = lane["speed"] * self.wave_scale * TILE_SIZE
                self.cars.add(v)

        # update logs
        for log in self.logs:
            log.update(dt)
        for log in self.logs.sprites():
            if (log.direction == -1 and log.rect.right < 0) or \
               (log.direction == +1 and log.rect.left > CANVAS_WIDTH):
                log.kill()

        # Continuous spawning of logs/turtles from the correct edge
        for lane in RIVER_LANES:
            row = lane["row"]
            dirn = lane.get("dir", 1)
            
            if row not in self.last_wood_spawn:
                self.last_wood_spawn[row] = 0
                
            # Use frame-counting instead of seconds for reliable intervals
            self.last_wood_spawn[row] += 1
            interval_s = lane.get("interval", 60) # Raw frame count from config
            
            if self.last_wood_spawn[row] >= interval_s:
                self.last_wood_spawn[row] = 0 # Reset exactly to avoid drift
                
                sprite_map = {"log": log_brown, "log_green": log_green_surf,
                              "turtle": turtle_surf}
                obj_type = random.choice(lane["objects"])
                width = 36 if obj_type == "log" else 40
                fn = sprite_map.get(obj_type, log_brown)
                
                # Spawn just outside the screen edge OPPOSITE to movement direction
                spawn_x = -TILE_SIZE // 2 if dirn == 1 else CANVAS_WIDTH + TILE_SIZE // 2
                
                flo = FloatingEntity(row, spawn_x, width, dirn, obj_type, fn)
                flo.speed = lane["speed"] * self.wave_scale * TILE_SIZE # <-- Fixed: multiply by TILE_SIZE!
                self.logs.add(flo)

        # check collision with cars (forgiving hitbox)
        frog_rect = pygame.Rect(
            int(self.frog.x - 12), int(self.frog.y - 12), 24, 24)
        for car in self.cars:
            # shrink car hitbox so more overlap is required
            car_hit = car.rect.inflate(-12, -12)
            if car_hit.colliderect(frog_rect):
                self.respawn()
                return

        # check wood riding
        self.check_wood_riding()

        # update frog position while on wood
        if self.frog.on_wood:
            self.frog.x += self.frog.on_wood.speed * \
                           self.frog.on_wood.direction * dt
            self.frog.y = self.frog.on_wood.rect.centery

        # check death in water (with grace period so grid-hop feels fair)
        if RIVER_START <= self.frog.row <= RIVER_END:
            if not self.frog.on_wood:
                self.in_water_grace -= dt
                if self.in_water_grace <= 0:
                    self.respawn()
                    return
        else:
            self.in_water_grace = 0.25  # reset grace when stepping on grass

        # check home slot landing
        self.frog_reaches_home()

    def draw(self, screen: pygame.Surface):
        """Draw the entire game to the given surface."""
        # background
        for row in range(ROWS):
            if row == HOME_ROW:
                color = HOME_BG
            elif RIVER_START <= row <= RIVER_END:
                color = BG_WATER
            else:
                color = BG_GRASS
            pygame.draw.rect(screen, color, (0, row * TILE_SIZE,
                                             CANVAS_WIDTH, TILE_SIZE))

        # home slots (highlight filled ones)
        for i, col in enumerate(HOME_SLOTS):
            rect = pygame.Rect(col * TILE_SIZE + 4, HOME_ROW * TILE_SIZE + 4,
                               TILE_SIZE - 8, TILE_SIZE - 8)
            color = HOME_ACTIVE if self.home_fills[i] else (50, 50, 50)
            pygame.draw.rect(screen, color, rect, border_radius=6)

        # spawn marker
        sx = 7 * TILE_SIZE + (TILE_SIZE // 2)
        sy = SPAWN_ROW * TILE_SIZE + (TILE_SIZE // 2)
        pygame.draw.circle(screen, WHITE, (sx, sy), 18, 3)

        # draw logs & turtles
        for log in self.logs:
            screen.blit(log.image, log.rect.topleft)

        # draw cars
        for car in self.cars:
            screen.blit(car.image, car.rect.topleft)

        # draw frog
        if self.state != STATE_DYING or int(pygame.time.get_ticks() / 100) % 2:
            img = frog_hop() if self.frog.moving else frog_idle()
            screen.blit(img, (int(self.frog.x - 16), int(self.frog.y - 16)))

        # overlays
        if self.state == STATE_WAVE_TRANSITION:
            overlay = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            font_big = pygame.font.SysFont(None, 72)
            text = font_big.render(f"Wave {self.wave} Complete!", True, FROG_GREEN)
            rect = text.get_rect(center=(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 3))
            screen.blit(text, rect)
            font_med = pygame.font.SysFont(None, 36)
            bonus_text = font_med.render(f"+{WAVE_BONUS} Bonus", True, WHITE)
            rect2 = bonus_text.get_rect(center=(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2))
            screen.blit(bonus_text, rect2)
        elif self.state == STATE_PAUSED:
            overlay = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            font_big = pygame.font.SysFont(None, 72)
            text = font_big.render("PAUSED", True, WHITE)
            rect = text.get_rect(center=(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2))
            screen.blit(text, rect)
            font_med = pygame.font.SysFont(None, 28)
            hint = font_med.render("Press P to Resume", True, WHITE)
            rect2 = hint.get_rect(center=(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 60))
            screen.blit(hint, rect2)

        # HUD (drawn by main loop)

    def handle_input(self, events):
        """Process keyboard input for frog movement."""
        if self.state == STATE_PAUSED:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.state = STATE_PLAYING
            return
        if self.state != STATE_PLAYING:
            return
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.state = STATE_PAUSED
                elif event.key == pygame.K_UP:
                    self.frog.move(0, -1)
                    self.play_sound("sfx_hop")
                elif event.key == pygame.K_DOWN:
                    self.frog.move(0, 1)
                    self.play_sound("sfx_hop")
                elif event.key == pygame.K_LEFT:
                    self.frog.move(-1, 0)
                    self.play_sound("sfx_hop")
                elif event.key == pygame.K_RIGHT:
                    self.frog.move(1, 0)
                    self.play_sound("sfx_hop")

    def draw_hud(self, screen: pygame.Surface):
        """Draw the score/lives/wave HUD."""
        y = CANVAS_HEIGHT + 5         # below canvas
        font = pygame.font.SysFont(None, 24)
        text = f"Score: {self.score}   Lives: {'♥' * self.lives}   Wave: {self.wave}"
        screen.blit(font.render(text, True, WHITE), (10, CANVAS_HEIGHT + 5))
