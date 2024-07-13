using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using BepInEx;
using BepInEx.Configuration;
using NineSolsAPI;
using UnityEngine;

namespace SkinMod;

// ReSharper disable once InconsistentNaming
internal record struct Rect(float x, float y, float width, float height);

// ReSharper disable once InconsistentNaming
internal record struct JsonSpriteInfo(string name, Rect rect);

internal record SpriteReplacementInfo(string AtlasName, Rect Rect, Sprite CachedSprite);

[BepInDependency(NineSolsAPICore.PluginGUID)]
[BepInPlugin(PluginInfo.PLUGIN_GUID, PluginInfo.PLUGIN_NAME, PluginInfo.PLUGIN_VERSION)]
public class SkinMod : BaseUnityPlugin {
    private SkinDataCache skinDataCache = new();

    private static string skinPath = Path.Join(Directory.GetParent(Application.dataPath)!.FullName, "ModData/Skins")!;

    private Dictionary<string, ISkinData> skins = [];
    private ConfigEntry<bool> enableSkin = null!;
    private ConfigEntry<string?> skinVariant = null!;

    private const string SkinVanilla = "No Skin";

    private void Awake() {
        Log.Init(Logger);
        RCGLifeCycle.DontDestroyForever(gameObject);

        Directory.CreateDirectory(skinPath);
        try {
            ReadSkins();

            enableSkin = Config.Bind("Skin", "Enable", true);
            var acceptableValues = new AcceptableValueList<string?>(skins.Keys.Concat([SkinVanilla]).ToArray());
            skinVariant = Config.Bind<string?>("Skin", "Variant", null, new ConfigDescription("", acceptableValues));
            skinVariant.SettingChanged += (_, _) => { OnSkinChange(); };
            OnSkinChange();
        } catch (Exception e) {
            ToastManager.Toast(e);
            throw;
        }


        Logger.LogInfo($"Plugin {PluginInfo.PLUGIN_GUID} is loaded!");
    }

    private void OnSkinChange() {
        if (skinVariant.Value is not { } skinName) return;

        if (skinName == SkinVanilla) {
            skinDataCache.SetSkin(null);
            return;
        }

        if (!skins.TryGetValue(skinName, out var skin)) {
            ToastManager.Toast($"Skin {skinName} does not exist!");
            return;
        }

        skinDataCache.SetSkin(skins[skinName]);
    }


    private void ReadSkins() {
        skins = Directory.GetFiles(skinPath)
            .Select<string, ISkinData?>(path => {
                if (path.EndsWith(".zip")) return new ZipSkinData(path);
                else if (Directory.Exists(path)) return new DirectorySkinData(path);
                else return null;
            })
            .OfType<ISkinData>()
            .Select(data => (meta: data.SkinJson(), data))
            .Where(skin => {
                if (skin.meta is not null) return true;
                ToastManager.Toast($"Could not read skin.json for {skin.data}");
                return false;
            })
            .ToDictionary(skin => skin.meta!.Value.name, skin => skin.data);
    }


    private void LateUpdate() {
        if (!enableSkin.Value) return;
        if (Player.i is not { } player) return;


        var spriteRenderer = player.PlayerSprite;
        var originalSprite = spriteRenderer.sprite;
        if (skinDataCache.GetSprite(originalSprite) is { } sprite) spriteRenderer.sprite = sprite;
    }


    private void OnDestroy() {
        skinDataCache.Dispose();
    }
}