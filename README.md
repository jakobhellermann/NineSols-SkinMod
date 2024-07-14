# Nine Sols SkinMod

## Installation
1. [Install BepInEx](https://docs.bepinex.dev/articles/user_guide/installation/index.html)
2. Download [NineSolsAPI.dll](https://github.com/nine-sols-modding/NineSolsAPI/releases/tag/v0.3.0) and put it in `GameFolder/BepInEx/plugins`
3. Download [SkinMod.dll](https://github.com/jakobhellermann/NineSols-SkinMod/releases) and put it in `GameFolder/BepInEx/plugins`
4. (Optional) Install [BepInEx ConfigurationManager](https://github.com/BepInEx/BepInEx.ConfigurationManager/releases/) to choose your skin in-game

## Install Skins

Choose a skin, download the `zip` and put it in `GameFolder/ModData/Skins`.

## Create Skins

Run [scripts/skin-recolor/src/extract_vanilla_skin.py](./scripts/skin-recolor/src/extract_vanilla_skin.py) to get the sprite atlases for Yee.
Paint over them, add a `skin.json` with the content `{ "name": "My Skin Name" }` next to them and zip everything.

If you want to just recolor the vanilla sprites, you can use [scripts/skin-recolor/src/create_recolored_skin.py](.sScripts/skin-recolor/src/create_recolored_skin.py) to replace some colors.
