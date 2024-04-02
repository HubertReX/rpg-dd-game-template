# Standard library imports
# import msvcrt

# Local folder imports
# from health_bar import HealthBar
from tile import player_marker
from weapon import fists, claws, jaws, short_bow

# INSTANT_INPUT = False


# ------------ parent class setup ------------
class Character:
    def __init__(
            self,
            name: str,
            health: int,
        ) -> None:
        self.name = name
        self.health = health
        self.health_max = health
        self.tile = "Player"

        self.weapon = fists

    def attack(self, target) -> None:
        if self.health <= 0:
            return
        target.health -= self.weapon.damage
        target.health = max(target.health, 0)
        # target.health_bar.update()
        # print(
        #     f"{self.name} dealt {self.weapon.damage} damage to "
        #     f"{target.name} with {self.weapon.name}"
        # )

    def __copy__(self):
        new_instance = self.__class__.__new__(self.__class__)
        new_instance.__dict__.update(self.__dict__)
        # Add any additional attributes that need to be copied
        return new_instance


# ------------ subclass setup ------------
class Player(Character):
    def __init__(self, start_x: int, start_y: int, name: str = "Player", health: int = 100) -> None:
        super().__init__(name=name, health=health)
        self.x: int = start_x
        self.y: int = start_y

        self.default_weapon = self.weapon
        # self.health_bar = HealthBar(self, color="green")
        # self.pos = [0, 0]
        self.marker = player_marker

        self.movement_options: dict[str, bool]

    def equip(self, weapon) -> None:
        self.weapon = weapon
        # print(f"{self.name} equipped a(n) {self.weapon.name}!")

    def drop(self) -> None:
        # print(f"{self.name} dropped the {self.weapon.name}!")
        self.weapon = self.default_weapon

    def move(self, x: int, y: int) -> None:
        self.x += x
        self.y += y

    def calculate_movement_options(self, width, height, map) -> None:
        x = self.x
        y = self.y
        # if x > 0 and y > 0:
        #     print(map[y-1][x-1].symbol,map[y-1][x].symbol,map[y-1][x+1].symbol)
        #     print(map[y-0][x-1].symbol,map[y-0][x].symbol,map[y-0][x+1].symbol)
        #     print(map[y+1][x-1].symbol,map[y+1][x].symbol,map[y+1][x+1].symbol)
        #     print("-"*10)
        self.movement_options = {
            "up": self.y > 0 and map[y-1][x] == "plains",  # can go up
            "down": self.y < height - 1 and map[y+1][x] == "plains",  # can go down
            "left": self.x > 0 and map[y-0][x-1] == "plains",  # can go left
            "right": self.x < width - 1 and map[y-0][x+1] == "plains" # can go right
        }
        # self.movement_options = {
        #     "up": self.pos[1] > 0 and map[y-0][x].name == "plains",  # can go up
        #     "down": self.pos[1] < height - 0 and map[y+0][x].name == "plains",  # can go down
        #     "left": self.pos[0] > 0 and map[y][x-0].name == "plains",  # can go left
        #     "right": self.pos[0] < width - 0 and map[y][x+0].name == "plains"  # can go right
        # }

    def get_movement_input(self) -> None:
        # choice = msvcrt.getch().decode('utf-8') if INSTANT_INPUT else input()
        choice = input()

        if self.movement_options["up"] and choice in ("w", "W"):
            self.y -= 1
        elif self.movement_options["down"] and choice in ("s", "S"):
            self.y += 1
        elif self.movement_options["left"] and choice in ("a", "A"):
            self.x -= 1
        elif self.movement_options["right"] and choice in ("d", "D"):
            self.x += 1


# ------------ subclass setup ------------
class Enemy(Character):
    def __init__(
            self,
            name: str,
            health: int,
            weapon=None,
        ) -> None:
        super().__init__(name=name, health=health)
        self.weapon = weapon

        # self.health_bar = HealthBar(self, color="red")

        enemies.append(self)


enemies = []
slime = Enemy("Slime", 10, jaws)
goblin = Enemy("Goblin", 20, short_bow)
spider = Enemy("Spider", 15, jaws)
rat = Enemy("Rat", 6, claws)
