#!/usr/bin/env python
from PIL import Image
import numpy as np
from pathlib import Path
import json
import shutil


def color_distance(data, target_color):
    return np.sqrt(np.sum((data - target_color) ** 2, axis=-1))


def adjust_brightness(color, factors):
    return np.clip(color * factors[:, :, np.newaxis], 0, 255).astype(np.uint8)


def replace_color(data, target_color, new_color, fuzz):
    target_color = np.array(target_color, dtype=np.float32)
    new_color = np.array(new_color, dtype=np.float32)

    distances = color_distance(data[:, :, :3].astype(np.float32), target_color)
    mask = distances <= fuzz

    brightness_factors = (np.mean(data[:, :, :3], axis=-1) + 1) / (
        np.mean(target_color) + 1
    )
    adjusted_color = adjust_brightness(new_color, brightness_factors)

    data[mask] = np.hstack((adjusted_color[mask], data[mask, 3][:, np.newaxis]))


input_dir = Path("out/skin_vanilla")


def recolor(name, out_dir, replacements, fuzz):
    out_dir.mkdir(exist_ok=True)

    with open(out_dir.joinpath("skin.json"), "w") as f:
        f.write(json.dumps({"name": name}, indent=4))

    for atlas in input_dir.iterdir():
        if atlas.name.endswith("txt"):
            continue

        out_path = out_dir.joinpath(atlas.name)
        print(name, out_path.name)

        img = Image.open(atlas).convert("RGBA")
        data = np.array(img)
        for replace, to in replacements:
            replace_color(data, replace, to, fuzz)
        result_img = Image.fromarray(data, "RGBA")
        result_img.save(out_path)


def create_skin(name, out, replacements):
    recolor(name, out, replacements, fuzz=50)
    shutil.make_archive(str(out), "zip", out)


out = Path("out")


create_skin(
    "red",
    out.joinpath(f"skin_red"),
    [
        ((231, 174, 51), (231, 51, 60)),  # cape
        ((66, 67, 49), (66, 53, 49)),  # cape border
        ((115, 87, 27), (66, 53, 49)),  # cape shadow
        ((168, 129, 40), (66, 53, 49)),  # cape shadow 2
        ((82, 203, 132), (106, 125, 185)),  # green highlight
    ],
)

create_skin(
    "purple",
    out.joinpath(f"skin_purple"),
    [
        ((231, 174, 51), (91, 52, 235)),  # cape
        ((66, 67, 49), (66, 53, 49)),  # cape border
        ((115, 87, 27), (66, 53, 49)),  # cape shadow
        ((168, 129, 40), (66, 53, 49)),  # cape shadow 2
        ((82, 203, 132), (106, 125, 185)),  # green highlight
    ],
)
