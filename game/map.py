# Standard library imports
import os
from random import randint
from typing import Any
import pygame

TILES_NAMES = [
    "plains", 
    "plain", 
    "forest",
    "pines",
    "mountain",
    "water",
    "player",
    "town",
    "road",
    "sand",
    "grass"
    ]
TILES = {}

class Map:
    def __init__(self, width, height, tiles_folder: str) -> None:
        self.width = width
        self.height = height
        self.tiles_folder = tiles_folder

        self.init_map_data: list[list[str]]
        self.map_data: list[list[str]]
        self.exploration_process: list[list[int]]

        self.generate_map()
        self.movement_options = {
            "up": "[W] - UP",
            "down": "[S] - DOWN",
            "left": "[A] - LEFT",
            "right": "[D] - RIGHT"
        }
        self.explored_tiles = ["player"]
        self.auto_reveal = True

    def load_images(self) -> None:
        for tile in TILES_NAMES:
            TILES[tile] = pygame.image.load(os.path.join(self.tiles_folder, f"{tile}.png")).convert_alpha()
            
        self.copy_map()

    def load_map(self, map: list[list[dict[str, Any]]], row: int, col: int) -> None:
        self.auto_reveal = False
        self.width = len(map[0])
        self.height = len(map)
        
        self.init_map_data = []
        self.exploration_process = []
        for y in range(self.height):
            map_row = []
            exploration_process = []
            for x in range(self.width):
                is_shown = int(map[y][x]["is_shown"])
                exploration_process.append(is_shown)
                renderer = map[y][x]["renderer"]
                # tile = TILES.get(renderer, "plain")
                if map[y][x]["symbol"] in ["🌲"]:
                    renderer = "pines"
                if map[y][x]["symbol"] in ["🗻", "⛰️"]:
                    renderer = "mountain"
                if map[y][x]["symbol"] in ["🏠"]:
                    renderer = "town"
                if map[y][x]["symbol"] in ["::"]:
                    renderer = "road"
                tile = renderer if renderer in TILES else "plain"
                map_row.append(tile)
            self.init_map_data.append(map_row)
            self.exploration_process.append(exploration_process)
        
        self.copy_map()
        # self.exploration_process = [[1 for _ in range(self.width)] for _ in range(self.height)]
        # self.reveal_map_all()
    
    def generate_map(self) -> None:
        self.generate_plains()
        self.generate_patch("forest", 3, 3, 7)
        self.generate_patch("pines", 3, 3, 7)
        self.generate_patch("mountain", 3, 3, 7)
        self.generate_patch("water", 2, 3, 9)
        self.generate_patch("town", 1, 3, 3)
        
        
    def generate_plains(self) -> None:
        self.init_map_data = [["plains" for _ in range(self.width)] for _ in range(self.height)]
        self.copy_map()

        self.exploration_process = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def generate_patch(
            self,
            tile: str,
            num_patches: int,
            min_size: int,
            max_size: int,
            irregular: int = True
    ) -> None:
        for _ in range(num_patches):
            size_y = randint(min_size, max_size)  # height of patch
            size_x = randint(min_size, max_size)  # width of patch
            start_y = randint(1, self.height - size_y - 1)  # top row
            start_x = randint(1, self.width - size_x - 1)  # start of row

            if irregular:
                raw_start_x = randint(3, self.width - max_size)  # start of row

            for i in range(size_y):
                if irregular:
                    size_x = randint(int(0.7 * max_size), max_size)  # randomized width of row
                    start_x = raw_start_x - randint(1, 2)  # randomized start of row
                for j in range(size_x):
                    self.init_map_data[start_y + i][start_x + j] = tile
        self.copy_map()


    def reveal_map_all(self) -> None:
        self.exploration_process = [[1 for _ in range(self.width)] for _ in range(self.height)]
        
        
    def reveal_map(self, pos: list[int]) -> None:
        if not self.auto_reveal:
            return
        
        x, y = pos
        sight_range = range(-2, 3)
        fov = [
            [0, 1, 1, 1, 0],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0],

        ]
        for y_index in sight_range:
            tile_y = y + y_index
            if 0 <= tile_y < self.height:
                for x_index in sight_range:
                    tile_x = x + x_index
                    if 0 <= tile_x < self.width and fov[y_index + 2][x_index + 2]:
                        self.exploration_process[tile_y][tile_x] = 1
                        revealed_tile = self.init_map_data[tile_y][tile_x]
                        if revealed_tile not in self.explored_tiles:
                            self.explored_tiles.append(revealed_tile)

    def update_map(self, pos: list[int], marker: str) -> None:
        x, y = pos
        self.copy_map()
        self.reveal_map(pos)
        # self.map_data[y][x] = marker

    def copy_map(self) -> None:
        self.map_data = [list(row) for row in self.init_map_data]
