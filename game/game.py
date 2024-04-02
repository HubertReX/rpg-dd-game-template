# Third-party imports
import asyncio
from copy import deepcopy
import math
import os
from random import choice, randint
from typing import Any
import pygame
# from pygame_emojis import load_emoji

# Local folder imports
try:
    from visual_interface.map import Map, TILES
except:
    from map import Map, TILES

from character import Player, Enemy, enemies
    
SPAWN_CHANCE = 10

# ------------ pygame mode setup ------------
class Game():
    def __init__(self, map_w: int = 10, map_h: int = 10, full_screen: bool = False, tiles_folder: str = "images", fonts_folder: str = "fonts") -> None:
        self.map_w = map_w
        self.map_h = map_h
        self.tiles_folder = tiles_folder
        self.fonts_folder = fonts_folder
        self.game_map = Map(map_w, map_h, self.tiles_folder)
        # self.game_map.reveal_map_all()
        self.player = Player(5, 5)
        self.full_screen = full_screen
        self.full_screen_width = 1080
        self.full_screen_height = 720
        self.windowed_screen_width = 1024
        self.windowed_screen_height = 768
        self.max_horizontal_tiles = 31
        self.max_vertical_tiles = 19
        self.FPS_CAP = 15
        self.flags: int = 0
        self.show_help: bool = False
        self.show_debug: bool = False

        # ----- initialize pygame
        pygame.init()
        self.clock = pygame.time.Clock()
        self.dt: float = 0.0
        # set tile attributes
        self.scale = 2
        self.tile_size = 16
        self.hud_height = 64 * self.scale
        self.screen_width: int = self.windowed_screen_width # self.tile_size * (self.map_w + 1) * self.scale 
        self.screen_height: int = self.windowed_screen_height # self.tile_size * (self.map_h + 1) * self.scale + self.hud_height

        self.darken_filter = pygame.Surface((self.tile_size, self.tile_size))
        gray = 80
        opacity = 255
        pygame.draw.rect(self.darken_filter, (gray, gray, gray, opacity),  (0,0, self.tile_size, self.tile_size))
        # self.darken_filter.set_colorkey((0,0,0))
        # setup screen
        if self.full_screen:
            self.flags |= pygame.FULLSCREEN
            self.screen_width = self.full_screen_width
            self.screen_height = self.full_screen_height
        else:
            self.flags = 0
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), self.flags)
        self.canvas = pygame.Surface((self.max_horizontal_tiles * self.tile_size, self.max_vertical_tiles * self.tile_size)).convert()
        self.map_background = pygame.Surface((self.screen_width, self.screen_height - self.hud_height)).convert_alpha()
        self.map_background.fill("yellow")
        map_frame = os.path.join(self.tiles_folder, "map_frame_512x320.png")
        # print(f"{map_frame=}")
        self.map_frame = pygame.transform.scale2x(pygame.image.load(map_frame)).convert_alpha()
        self.hud_frame = pygame.transform.scale2x(pygame.image.load(os.path.join(self.tiles_folder, "hud_frame_512x64.png"))).convert_alpha()
        
        # Load the emoji as a pygame.Surface
        # self.hero = load_emoji('🧌', (self.tile_size * self.scale, self.tile_size * self.scale))
        # self.hero.set_colorkey((0,0,0))

        # load images of tiles
        self.game_map.load_images()
        TILES["player"].set_colorkey((0,0,0))


        self.enemy_in_combat: Enemy | None = None

    def load_map(self, map: list[list[dict[str, Any]]], row: int, col: int) -> None:
        self.game_map.load_map(map, row, col)
        self.map_h = self.game_map.height
        self.map_w = self.game_map.width

        self.screen_width: int = self.windowed_screen_width # self.tile_size * (self.map_w + 1) * self.scale 
        self.screen_height: int = self.windowed_screen_height # self.tile_size * (self.map_h + 1) * self.scale + self.hud_height

        # setup screen
        if self.full_screen:
            self.flags |= pygame.FULLSCREEN
            self.screen_width = self.full_screen_width
            self.screen_height = self.full_screen_height
        else:
            self.flags = 0
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), self.flags)
        self.canvas = pygame.Surface((self.max_horizontal_tiles * self.tile_size, self.max_vertical_tiles * self.tile_size)).convert()
        self.map_background = pygame.Surface((self.screen_width, self.screen_height - self.hud_height)).convert_alpha()
        self.map_background.fill("brown")

    def toggle_fullscreen(self):
        self.full_screen = not self.full_screen
        
        if self.full_screen:
            self.flags |= pygame.FULLSCREEN
            self.screen_width = self.full_screen_width
            self.screen_height = self.full_screen_height
        else:
            self.flags = 0
            self.screen_width: int = self.windowed_screen_width # self.tile_size * (self.map_w + 1) * self.scale 
            self.screen_height: int = self.windowed_screen_height # self.tile_size * (self.map_h + 1) * self.scale + self.hud_height
            
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), self.flags)

    async def run(self) -> None:
        """
        Running the game in Pygame mode means continuous cycles.
        The logic is different and a bit more complicated.
        """
        while True:
            # ----- checking for any event like key presses
            self.check_events()
            self.main_game_loop(self.player.x, self.player.y)
            await asyncio.sleep(0)

    def main_game_loop(self, x: int, y: int):
        # self.check_events()
        self.player.x = x
        self.player.y = y
        
        # ----- break out of loop if the player health pool is empty
        if self.player.health <= 0:
            self.display()
            self.display_ui()
            self.draw_text("Game Over", [self.screen_width // 2, self.screen_height // 2])
            pygame.display.update()
            return
        # ----- calculate movement possibilities
        self.player.calculate_movement_options(self.map_w, self.map_h, self.game_map.map_data)

            # ----- update map with player (reveal nearby tiles)
        self.game_map.update_map([x, y], self.player.tile)

            # ----- display the map with the tiles
        self.display()

            # ----- display combat & non-combat ui
        self.display_ui()

            # ----- update the window
        pygame.display.update()
        # self.clock.tick()
        self.dt = self.clock.tick(self.FPS_CAP) / 1000


    def spawn_enemy(self, pos: list[int]) -> Enemy | None:
        x, y = pos
        chance = randint(1, 100)
        tile = self.game_map.init_map_data[y][x]
        if chance < SPAWN_CHANCE and tile != "water":
            return deepcopy(choice(enemies))

    def check_events(self) -> str:
        res = ""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()           
            # res = self.check_movement_inputs()
            elif event.type == pygame.KEYDOWN:
                # ----- if an enemy is present, only the enter key is allowed
                if self.enemy_in_combat:
                    if event.key in [pygame.K_F8, pygame.K_q]:
                        pygame.quit()
                        exit()
                    elif event.key == pygame.K_h:
                        self.show_help = not self.show_help
                    elif event.key == pygame.KSCAN_APOSTROPHE:
                        self.show_debug = not self.show_debug
                    elif event.key == pygame.K_RETURN:
                        # print("next_turn")
                        self.next_turn()
                # ----- if there is no enemy, the player can move the available directions
                else:
                    res = self.check_movement_inputs()
                    if res != "":
                        self.enemy_in_combat = self.spawn_enemy([self.player.x , self.player.y])
        
        return res

    def check_movement_inputs(self) -> str:
        res = ""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_F8] or keys[pygame.K_q] or keys[pygame.K_ESCAPE]:
            pygame.quit()
            exit()
        if keys[pygame.K_r]:
            self.game_map.reveal_map_all()
        if keys[pygame.K_f]:
            self.toggle_fullscreen()
        if keys[pygame.K_g]:
            self.game_map.generate_map()
            self.canvas.fill("black")
        if keys[pygame.K_h]:
            self.show_help = not self.show_help
            # print()
        if keys[pygame.K_BACKQUOTE]:
            self.show_debug = not self.show_debug
        if self.player.health <= 0:
            return res

        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.player.movement_options.get("up"):
            self.player.y -= 1
            self.player.y = max(0, self.player.y)
            res = "W"
            # self.player.pos[1] -= 1
            # self.enemy_in_combat = self.spawn_enemy(self.player.pos)
        if (keys[pygame.K_s] or keys[pygame.K_DOWN] and self.player.movement_options.get("down")):
            self.player.y += 1
            self.player.y = min(self.map_h-1, self.player.y)
            res = "S"
            # self.player.pos[1] += 1
            # self.enemy_in_combat = self.spawn_enemy(self.player.pos)
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.player.movement_options.get("left"):
            self.player.x -= 1
            self.player.x = max(0, self.player.x)
            res = "A"
            # self.player.pos[0] -= 1
            # self.enemy_in_combat = self.spawn_enemy(self.player.pos)
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.player.movement_options.get("right"):
            self.player.x += 1
            self.player.x = min(self.map_w-1, self.player.x)
            res = "D"
            # self.player.pos[0] += 1
            # self.enemy_in_combat = self.spawn_enemy(self.player.pos)
        return res

    def display(self) -> None:
        self.screen.fill("black")
        # ----- blit each tile onto the canvas if it's explored
        
        if self.game_map.width > self.max_horizontal_tiles:
            start_x = self.player.x - (self.max_horizontal_tiles // 2)
            if start_x < 0:
                start_x = 0
            end_x = start_x + self.max_horizontal_tiles
            if end_x > self.game_map.width:
                end_x = self.game_map.width
                start_x = end_x - self.max_horizontal_tiles
        else:
            start_x = 0
            end_x = self.game_map.width
            
        if self.game_map.height > self.max_vertical_tiles:
            start_y = self.player.y - (self.max_vertical_tiles // 2)
            if start_y < 0:
                start_y = 0
            end_y = start_y + self.max_vertical_tiles
            if end_y > self.game_map.height:
                end_y = self.game_map.height
                start_y = end_y - self.max_vertical_tiles
        else:
            start_y = 0
            end_y = self.game_map.height
            
        self.canvas.fill("black")
        # for i, row in enumerate(self.game_map.map_data):
        for i in range(start_y, end_y):
            row = self.game_map.map_data[i]
            # for j, tile in enumerate(row):
            for j in range(start_x, end_x):
                tile = row[j]
                if self.game_map.exploration_process[i][j]:
                    # print(tile.name)
                    # self.canvas.blit(tile.image, (j * self.tile_size, i * self.tile_size))
                    if tile not in TILES:
                        print(f"tile {tile} not found")
                    self.canvas.blit(TILES[tile], ((j-start_x) * self.tile_size, (i-start_y) * self.tile_size))
                    if j == self.player.x and i == self.player.y:
                        self.canvas.blit(TILES["player"], ((j-start_x) * self.tile_size, (i-start_y) * self.tile_size))
                    distance =  math.hypot(self.player.x - j, self.player.y - i)
                    # if (i < self.player.y - 2 or i > self.player.y + 2 or j < self.player.x - 2 or j > self.player.x + 2) :
                    if distance > 2.5:
                        self.canvas.blit(self.darken_filter, ((j-start_x) * self.tile_size, (i-start_y) * self.tile_size), special_flags=pygame.BLEND_MULT)
        # ----- blit the canvas to the screen
        self.screen.blit(self.map_background, (0, 0))
        self.screen.blit(self.map_frame, (0, 0))
        self.screen.blit(self.hud_frame, (0, self.screen_height - self.hud_height))
        self.screen.blit(pygame.transform.scale2x(self.canvas), (self.tile_size, self.tile_size))
        # self.screen.blit(self.hero, (self.tile_size + self.player.x * self.tile_size * self.scale, self.tile_size + self.player.y * self.tile_size * self.scale))

    def display_ui(self) -> None:
        if self.show_debug:
            self.draw_text(f"FPS   : {self.clock.get_fps():6.2f} {self.dt:6.4f}", [10,  40], alignment="left")
            self.draw_text(f"Player: {self.player.x:3d}x{self.player.y:3d}", [10,  70], alignment="left")
            self.draw_text(f"Map   : {self.game_map.width:3d}x{self.game_map.height:3d}", [10,  100], alignment="left")
            self.draw_text(f"Screen: {self.screen_width:3d}x{self.screen_height:3d}", [10,  130], alignment="left")
        
        self.draw_text(self.player.name, [self.screen_width // 2, self.screen_height - 110])
        self.draw_health_bar(self.player.health, self.player.health_max, [40, 200, 40], self.screen_height - 95)

        self.draw_text("[h] - help", [self.screen_width - 240, self.screen_height - 30], "left")
        if self.enemy_in_combat:
            self.draw_text("[ENTER] - ATTACK", [self.screen_width - 240, self.screen_height - 105], "left")
            self.draw_text(self.enemy_in_combat.name, [self.screen_width // 2, self.screen_height - 55])
            self.draw_health_bar(self.enemy_in_combat.health, self.enemy_in_combat.health_max, [200, 40, 40], self.screen_height - 40)
        elif self.show_help:
            self.draw_text("[Esc], [q] - quit", [10, (0 * 30) + self.screen_height - 110], "left")
            self.draw_text("[g] - generate map", [10, (1 * 30) + self.screen_height - 110], "left")
            self.draw_text("[r] - reveal map", [10, (2 * 30) + self.screen_height - 110], "left")
            # self.draw_text("[f] - full screen", [10, (3 * 30) + self.screen_height - 110], "left")
            self.draw_text("[`] - debug info", [10, (3 * 30) + self.screen_height - 110], "left")
        else:
            for index, (direction, value) in enumerate(self.game_map.movement_options.items()):
                if self.player.movement_options.get(direction):
                    self.draw_text(value, [25, (index * 30) + self.screen_height - 110], "left")

    def next_turn(self) -> None:
        # ----- prompt a single attack
        # print("player attack")
        self.player.attack(self.enemy_in_combat)
        # print("enemy attack")
        self.enemy_in_combat.attack(self.player)
        # ----- reset the attribute if either of the combatants are dead
        if self.player.health <= 0 or self.enemy_in_combat.health <= 0:
            self.enemy_in_combat = None
        # print(f"{self.enemy_in_combat==None}")

    def draw_text(self, text: str, pos: list[int], alignment=None, size=30, color="cyan") -> None:
        # font = pygame.font.Font(None, 36)
        font = pygame.font.Font(os.path.join(self.fonts_folder, "font.ttf"), size)

        text_surface = font.render(text, True, color).convert_alpha()
        text_rect = text_surface.get_rect(center=pos)
        if alignment == "left":
            text_rect.midleft = pos
        elif alignment == "right":
            text_rect.midright = pos
        elif alignment == "top":
            text_rect.midtop = pos
        self.screen.blit(text_surface, text_rect)

    def draw_health_bar(self, hp: int, max_hp: int, color: list[int], y: int) -> None:
        length = 200
        width = max(hp / max_hp * length, 1)

        bar = pygame.Surface((width, 24)).convert_alpha()
        bar.fill(color)
        bar_rect = bar.get_rect(midleft=((self.screen_width / 2 - length / 2), y + 12))

        full_bar = pygame.Surface((length, 24)).convert_alpha()
        full_bar.fill("gray")
        full_bar_rect = full_bar.get_rect(midleft=((self.screen_width / 2 - length / 2), y + 12))

        outline = pygame.Surface((length, 24)).convert_alpha()
        outline.fill("black")
        outline_rect = full_bar.get_rect(center=((self.screen_width / 2), y + 12))

        self.screen.blit(full_bar, full_bar_rect)
        self.screen.blit(bar, bar_rect)
        pygame.draw.rect(self.screen, "black", outline_rect, width=3)
        self.draw_text(f"{hp}/{max_hp}", [self.screen_width // 2, y], "top", 24, "black")

