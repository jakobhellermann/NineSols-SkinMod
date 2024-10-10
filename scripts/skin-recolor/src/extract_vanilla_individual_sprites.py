#!/usr/bin/env python
from pathlib import Path

from UnityPy.environment import Environment
from UnityPy.classes import Sprite, SpriteAtlas
from UnityPy.enums import ClassIDType

path = Path("/home/jakob/.local/share/Steam/steamapps/common/Nine Sols/NineSols_Data/")
out = Path("out/individual_sprites")
out.mkdir(exist_ok=True)

if not path.exists():
    raise Exception(f"{path} does not exist")


def interest_in_sprite(name: str):
    return "Yee" in name and name not in ["HoHoYee_無極之地Bk"]


atlases: set[SpriteAtlas] = set()

# files = ["resources.assets", *[f"sharedassets{i}.assets" for i in range(0, 116)]]
files = ["resources.assets"]

for filename in files:
    # load file
    assets = Environment(str(path.joinpath(filename))).file

    # iterate over every object in the file
    for obj in assets.objects.values():
        # if it's a sprite
        if obj.type == ClassIDType.Sprite:
            sprite: Sprite = obj.read()
            sprite_name = sprite.m_Name

            # if the sprite name interests us
            if interest_in_sprite(sprite_name):
                print(sprite_name)
                # export png
                path = out.joinpath(sprite_name).with_suffix(".png")
                sprite.image.save(str(path))
