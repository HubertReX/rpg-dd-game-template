# Standard library imports
import asyncio
import os

# Local folder imports
from game import Game

if __name__ == "__main__":
    game = Game(34, 19, full_screen=False, tiles_folder=os.path.join("images"), fonts_folder=os.path.join("fonts"))
    asyncio.run(game.run())
