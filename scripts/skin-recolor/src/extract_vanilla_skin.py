#!/usr/bin/env python
from pathlib import Path

from PIL import Image
from UnityPy.environment import Environment
from UnityPy.classes import Sprite, SpriteAtlas
from UnityPy.export.SpriteHelper import get_image
from UnityPy.enums import ClassIDType
import json

export_textures = True
write_atlas_info = False

path = Path("/home/jakob/.local/share/Steam/steamapps/common/Nine Sols/NineSols_Data/")
out = Path("out")

if not path.exists():
    raise Exception(f"{path} does not exist")


def interest_in_sprite(name: str):
    return "Yee" in name and name not in ["HoHoYee_無極之地Bk"]


atlases: set[SpriteAtlas] = set()

# files = ["resources.assets", *[f"sharedassets{i}.assets" for i in range(0, 116)]]
files = ["resources.assets"]

# for i in range(0, 110):
for filename in files:
    assets = Environment(str(path.joinpath(filename))).file

    for obj in assets.objects.values():
        if obj.type == ClassIDType.Sprite:
            sprite: Sprite = obj.read()
            sprite_name = sprite.m_Name
            atlas = sprite.m_SpriteAtlas.get_obj()
            if interest_in_sprite(sprite_name):
                if atlas is not None:
                    atlases.add(atlas.read())

new = {}
for atlas in atlases:
    filename = atlas.assets_file.name
    list = new[filename] = new.get(filename, [])
    list.append(atlas.name)

out.mkdir(exist_ok=True)

# out_json = dict(sorted(new.items()))
# with open(out.joinpath("out.json"), "w") as f:
#     f.write(json.dumps(out_json, ensure_ascii=False, indent=4))

out_atlases = out.joinpath("skin_vanilla")
out_atlases.mkdir(exist_ok=True)


sprite_lookup = {}
for atlas in atlases:
    print(atlas.name)
    atlas_sprites = []
    for i, render_data in enumerate(atlas.m_RenderDataMap.values()):
        name = atlas.m_PackedSpriteNamesToIndex[i]
        if interest_in_sprite(name):
            atlas_sprites.append(
                {
                    "name": name,
                    "rect": render_data.textureRect.__dict__,
                }
            )
    sprite_lookup[atlas.name] = atlas_sprites

    if export_textures:
        textures = set(
            data.texture.get_obj() for data in atlas.m_RenderDataMap.values()
        )
        alpha_textures = set(
            data.alphaTexture.get_obj() for data in atlas.m_RenderDataMap.values()
        )
        (texture,) = textures
        (alpha_texture,) = alpha_textures
        assert alpha_texture is None
        img = get_image(texture, texture, None)
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        out_path = out_atlases.joinpath(atlas.name).with_suffix(".png")
        img.save(out_path)

if write_atlas_info:
    with open(out.joinpath("atlas_info.json"), "w") as f:
        f.write(json.dumps(sprite_lookup, ensure_ascii=False, indent=2))

print("Done")
