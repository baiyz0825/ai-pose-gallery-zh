#!/usr/bin/env python3
"""Generate the AI skill catalogs from the repository's canonical data JSON files.

Run from the repository root after data/*.json changes. The generated unified
skills/catalog.jsonl is intentionally complete, including gia-anime and shisei.
"""
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SKILLS = ROOT / "skills"


def read(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def rows():
    poses = read("pose-zh.json")
    portraits = read("portrait-zh.json")
    costumes = []
    for name in ("costume-zh.json", "costume-anime-zh.json", "costume-gia-anime-zh.json", "costume-shisei-zh.json"):
        costumes.extend(read(name))
    for x in poses:
        yield {"lib": "pose", "id": x["id"], "system": x.get("体系", ""), "category": x.get("分类", ""), "name": x.get("姿势名称", ""), "angle": x.get("角度", ""), "path": x.get("原图", ""), "thumb": x.get("缩略图", ""), "search": x.get("检索", "")}
    for x in portraits:
        yield {"lib": "portrait", "id": x["id"], "section": x.get("分区", ""), "hair_length": x.get("发长", ""), "style": x.get("发型名称", ""), "name": x.get("标题", ""), "path": x.get("原图", ""), "thumb": x.get("缩略图", ""), "search": x.get("检索", "")}
    for x in costumes:
        yield {"lib": "costume", "id": x["id"], "source": x.get("source", "base"), "category": x.get("分类", ""), "name": x.get("服装名称", ""), "tags": x.get("标签", []), "keywords": x.get("关键词", ""), "path": x.get("原图", ""), "thumb": x.get("缩略图", ""), "search": x.get("检索", "")}


def write_csv(path, fields, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(data)


def main():
    all_rows = list(rows())
    out = SKILLS / "catalog.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for x in all_rows:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

    poses = [x for x in all_rows if x["lib"] == "pose"]
    portraits = [x for x in all_rows if x["lib"] == "portrait"]
    costumes = [x for x in all_rows if x["lib"] == "costume"]
    pose_defs = {
        "pose-reference-all": poses,
        "pose-reference-standard": [x for x in poses if x["system"] == "全身单人・标准系"],
        "pose-reference-sexy": [x for x in poses if x["system"] == "全身单人・性感系"],
        "pose-reference-couple": [x for x in poses if x["system"] == "双人缠绵"],
        "pose-reference-upper": [x for x in poses if x["system"] == "上半身单人"],
    }
    for name, data in pose_defs.items():
        write_csv(SKILLS / name / "references/catalog.csv", ["id", "体系", "分类", "姿势名称", "角度", "图片"], [{"id": x["id"], "体系": x["system"], "分类": x["category"], "姿势名称": x["name"], "角度": x["angle"], "图片": x["path"]} for x in data])
    write_csv(SKILLS / "portrait-reference/references/catalog.csv", ["id", "分区", "发长", "发型名称", "标题", "图片"], [{"id": x["id"], "分区": x["section"], "发长": x["hair_length"], "发型名称": x["style"], "标题": x["name"], "图片": x["path"]} for x in portraits])
    costume_base = [x for x in costumes if x["source"] == "base"]
    costume_sexy = [x for x in costume_base if "性感" in x["category"] or "内衣" in x["category"]]
    costume_real = [x for x in costume_base if x not in costume_sexy]
    costume_defs = {
        "costume-reference": costume_real,
        "costume-reference-sexy": costume_sexy,
        "costume-reference-anime": [x for x in costumes if x["source"] == "charadb"],
        "costume-reference-gia-anime": [x for x in costumes if x["source"] == "gia-anime"],
        "costume-reference-shisei": [x for x in costumes if x["source"] == "shisei"],
    }
    for name, data in costume_defs.items():
        write_csv(SKILLS / name / "references/catalog.csv", ["id", "分类", "服装名称", "标签", "英文关键词", "图片"], [{"id": x["id"], "分类": x["category"], "服装名称": x["name"], "标签": " ".join(x["tags"] if isinstance(x["tags"], list) else [str(x["tags"])]), "英文关键词": x["keywords"], "图片": x["path"]} for x in data])
    print(f"generated {len(all_rows)} unified records")

if __name__ == "__main__":
    main()
