#!/usr/bin/env python
from pathlib import Path
import shutil
import json

from UnityPy.environment import Environment
from UnityPy.classes import Sprite, SpriteAtlas
from UnityPy.enums import ClassIDType


# configuration
path = Path("/home/uni/.local/share/Steam/steamapps/common/Nine Sols/NineSols_Data/")
out = Path("out")

interest_includes = ["Yee"]
interest_excludes = [
    "HoHoYee_無極之地Bk",
    "ControlRoom_YeeScreen",
    "2048light",
    "BackgroundYee",
]

files = ["resources.assets"]
# files = ["resources.assets", *[f"sharedassets{i}.assets" for i in range(0, 116)]]

if not path.exists():
    raise Exception(f"{path} does not exist")


def interest_in_sprite(name: str):
    for include in interest_includes:
        if include not in name:
            return False
    for exclude in interest_excludes:
        if exclude in name:
            return False

    return True


# utils


def dedup_by(values, by):
    return [
        v1
        for i, v1 in enumerate(values)
        if not any((by(v1) == by(v2) for v2 in values[:i]))
    ]


def commonprefix(m):
    if not m:
        return ""
    s1 = min(m)
    s2 = max(m)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]
    return s1


def infer_atlas_name(atlas: SpriteAtlas):
    prefix = commonprefix(set(atlas.m_PackedSpriteNamesToIndex))
    return (
        prefix.strip("_")
        if prefix
        else atlas.name.replace("_master_atlas", "").replace("2020", "")
    )


# collect sprites

atlases: dict[SpriteAtlas, list[Sprite]] = {}
for filename in files:
    assets = Environment(str(path.joinpath(filename))).file

    for obj in assets.objects.values():
        if obj.type == ClassIDType.Sprite:
            sprite: Sprite = obj.read()
            sprite_name = sprite.m_Name
            atlas = sprite.m_SpriteAtlas.get_obj()

            if interest_in_sprite(sprite_name):
                if atlas is not None:
                    atlas = atlas.read()
                    atlases[atlas] = atlases.get(atlas, [])
                    # atlases[atlas].append(sprite)
                else:
                    atlases[None] = atlases.get(None, [])
                    atlases[None].append(sprite)

for atlas in atlases:
    if atlas is None:
        continue

    sprites_deduped = dedup_by(
        [x.read() for x in atlas.m_PackedSprites], lambda x: x.name
    )
    atlases[atlas].extend(sprites_deduped)


out.mkdir(exist_ok=True)
out_skin = out.joinpath("skin_vanilla")
out_skin.mkdir(exist_ok=True)

for atlas in atlases:
    atlas_name = infer_atlas_name(atlas) if atlas else "uncategorized"

    out_skin_atlas = out_skin.joinpath(atlas_name)
    out_skin_atlas.mkdir(exist_ok=True)

    for sprite in atlases[atlas]:
        out_skin_atlas_texture = out_skin_atlas.joinpath(sprite.name).with_suffix(
            ".png"
        )
        if not out_skin_atlas_texture.exists():
            sprite.image.save(str(out_skin_atlas_texture))


skin_json = {
    "version": "1",
    "name": "vanilla",
}

with open(out_skin.joinpath("skin.json"), "w") as f:
    json.dump(skin_json, f, indent=4)

shutil.make_archive(out_skin, "zip", out_skin)
