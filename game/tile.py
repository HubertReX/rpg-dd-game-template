# Standard library imports
import os

# Third-party imports
import pygame

# Local folder imports
# from color import Color as c


class Tile:
    def __init__(self, name: str) -> None:
        # self.symbol = symbol
        self.name = name
        # self.image = None
        # self.legend = f"{symbol} {name.upper()}"

        # self.colored_symbol = f"{color}{symbol}{c.ANSI_RESET}"
        # self.colored_name = f"{color}{name.upper()}{c.ANSI_RESET}"
        # self.colored_legend = f"{self.colored_symbol} {self.colored_name}"

    # def load_image(self):
    #     self.image = pygame.image.load(os.path.join("images", f"{self.name}.png")).convert_alpha()

def load_image(name):
    return pygame.image.load(os.path.join("images", f"{name}.png")).convert_alpha()
    # print(self.name, self.image.get_height())
        


plains = Tile("plains")
forest = Tile("forest")
pines = Tile("pines")
mountain = Tile("mountain")
water = Tile("water")
player_marker = Tile("player")
empty = Tile("???")
town = Tile("town")

TILES_NAMES = ["plains", "forest", "pines", "mountain", "water", "player", "town"]
TILES = {}
