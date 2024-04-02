# RPG D&D game template

## Disclaimer

Main code base is taken from Adrian (Ork Slayer Gamedev):

[GitHub Repo](https://github.com/orkslayergamedev/roguelike-ascii-vs-pygame)

check out his great [YT](https://www.youtube.com/@orkslayergamedev/) tutorials!

## Features

* transparent sprites (player)
* automatic/procedural map generation (simple patch system with some randomization)
* several enemies with different weapons (no sprites yet)
* map scrolling
* fog of war
* simple collision detection (only grassland is walkable)
* runs in desktop and in web browser as well (thanks to [pygbag](https://pygame-web.github.io/) lib)

## TODO

* enemy sprites
* touchscreen controls
* custom pygbag template

## Installation

* install

```bash
pip install -r requirements.txt
```

## Running

Desktop mode:

```bash
python main.py
```

Browser mode:

```bash
pygbag src
```

## Deploying

### To [itch.io](itch.io)

full instruction [here](https://pygame-web.github.io/wiki/pygbag/itch.io/)

```bash
pygbag --archive src
```

upload build/web.zip to [itch.io](itch.io)

### To GitHub pages

full instruction [here](https://pygame-web.github.io/wiki/pygbag/github.io/)
