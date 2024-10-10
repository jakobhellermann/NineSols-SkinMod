using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using NineSolsAPI.Utils;
using UnityEngine;

namespace SkinMod;

// ReSharper disable once InconsistentNaming
public record struct SkinMeta(string name);

public class SkinDataCache : IDisposable {
    private Dictionary<string, (string, Rect)> spriteLocations = new();

    private static string[] imageExtensions = ["png", "jpg", "jpeg"];

    public SkinDataCache() {
        var json =
            AssemblyUtils.GetEmbeddedJson<Dictionary<string, JsonSpriteInfo[]>>("SkinMod.Resources.atlas_info.json")!;

        foreach (var (atlasName, atlasSprites)in json)
        foreach (var spriteInfo in atlasSprites)
            spriteLocations[spriteInfo.name] = (atlasName, spriteInfo.rect);
    }

    private ISkinData? skinData;

    private Dictionary<string, Texture2D?> atlasCache = new();
    private Dictionary<string, Sprite?> spriteCache = new();

    public void SetSkin(ISkinData? skinData) {
        this.skinData = skinData;
        atlasCache.Clear();
        spriteCache.Clear();
    }


    public void Dispose() {
        skinData?.Dispose();
    }

    private Texture2D? GetAtlas(ISkinData skinData, string atlasName) {
        if (atlasCache.TryGetValue(atlasName, out var atlas)) return atlas;
        var newAtlas = GetAtlasInner(skinData, atlasName);
        atlasCache[atlasName] = newAtlas;
        return newAtlas;
    }

    private Texture2D? GetAtlasInner(ISkinData skinData, string atlasName) {
        using var stream = skinData.OpenFile(atlasName, imageExtensions);
        if (stream is null) return null;
        using var reader = new MemoryStream();
        stream.CopyTo(reader);

        var texture = new Texture2D(2, 2);
        texture.LoadImage(reader.GetBuffer());

        return texture;
    }

    /*public Sprite? GetSprite(Sprite original) {
        if (spriteCache.TryGetValue(original.name, out var cachedSprite)) return cachedSprite;

        if (!spriteLocations.TryGetValue(original.name, out var location)) return null;

        var (atlasName, rect) = location;
        if (GetAtlas(atlasName) is not { } atlas) return null;


        var sprite = Sprite.Create(
            atlas,
            new UnityEngine.Rect(rect.x, rect.y, rect.width, rect.height),
            original.pivot,
            original.pixelsPerUnit
        );
        sprite.name = original.name;
        spriteCache[original.name] = sprite;

        return sprite;
    }
*/

    public Sprite? GetSprite(Sprite original) {
        if (skinData is null) return null;
        if (spriteCache.TryGetValue(original.name, out var cachedSprite)) return cachedSprite;
        var sprite = GetSpriteInner(skinData, original);
        spriteCache[original.name] = sprite;
        return sprite;
    }

    private Sprite? GetSpriteInner(ISkinData skinData, Sprite original) {
        if (!spriteLocations.TryGetValue(original.name, out var location)) return null;

        var (atlasName, rect) = location;
        if (GetAtlas(skinData, atlasName) is not { } atlas) return null;
        var uRect = new UnityEngine.Rect(rect.x, rect.y, rect.width, rect.height);
        var empty = new Texture2D(atlas.width, atlas.height);

        if (!original.name.StartsWith("HoHoYee_Standingidle4")) return null;

        var pivot = original.pivot / original.rect.size;
        var sprite = Sprite.Create(
            atlas,
            // empty,
            original.textureRect,
            pivot,
            8,
            0, SpriteMeshType.Tight, original.border, false, []
        );

        var factor = original.textureRect.size / original.rect.size;

        /*sprite.OverrideGeometry(original.vertices.Select(x => {
            var delta = pivot * sprite.textureRect.size;
            var remapped = x * 8f * factor + delta;
            return new Vector2(
                Mathf.Clamp(remapped.x, 0, sprite.rect.width),
                Mathf.Clamp(remapped.y, 0, sprite.rect.height)
            );
        }).ToArray(), original.triangles);*/

        var physicsShapes = new List<Vector2[]>(original.GetPhysicsShapeCount());
        for (var i = 0; i < original.GetPhysicsShapeCount(); i++) {
            List<Vector2> outShape = [];
            original.GetPhysicsShape(i, outShape);
            physicsShapes.Add(outShape.ToArray());
        }

        sprite.OverridePhysicsShape(physicsShapes);

        return sprite;
    }
}

public interface ISkinData : IDisposable {
    Stream? OpenFile(string filename);

    Stream? OpenFile(string filestem, string[] extensions) {
        foreach (var extension in extensions) {
            var entry = OpenFile($"{filestem}.{extension}");
            if (entry is not null) return entry;
        }

        return null;
    }

    SkinMeta? SkinJson() {
        using var file = OpenFile("skin.json");
        if (file is null) return null;
        return JsonUtils.DeserializeStream<SkinMeta>(file);
    }
}

internal class DirectorySkinData(string dirPath) : ISkinData {
    // todo: fix path traversal?
    public Stream? OpenFile(string filename) {
        try {
            return File.OpenRead(Path.Combine(dirPath, filename));
        } catch (FileNotFoundException) {
            return null;
        }
    }

    public override string ToString() => $"DirectorySkinData({dirPath}";

    public void Dispose() {
    }
}

internal class ZipSkinData : ISkinData {
    private ZipArchive zipArchive;
    private string path;

    public ZipSkinData(string path) {
        var zip = ZipFile.OpenRead(path);
        zipArchive = zip;
        this.path = path;
    }

    public void Dispose() {
        zipArchive.Dispose();
    }

    public Stream? OpenFile(string filename) {
        var entry = zipArchive.GetEntry(filename);
        return entry?.Open();
    }


    public override string ToString() => $"ZipSkinData({path}";
}