#!/usr/bin/env python3
"""Validate structural and non-negotiable constraints of this skill."""

from __future__ import annotations

import struct
import sys
from pathlib import Path


ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("not a valid PNG")
    return struct.unpack(">II", header[16:24])


required_files = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/参考图索引.md",
    "references/版式与提示词模板.md",
    "references/验收标准.md",
]
required_files += [f"assets/posters/{index:02d}.png" for index in range(1, 5)]
required_files += [f"assets/covers/{index:02d}.png" for index in range(1, 5)]

errors: list[str] = []
for relative in required_files:
    if not (ROOT / relative).is_file():
        errors.append(f"missing required file: {relative}")

if not errors:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    template = (ROOT / "references/版式与提示词模板.md").read_text(encoding="utf-8")
    rubric = (ROOT / "references/验收标准.md").read_text(encoding="utf-8")

    skill_invariants = [
        "$fugumaozhan",
        "$imagegen",
        "禁止",
        "纯提示词",
        "assets/posters/01.png",
        "assets/covers/01.png",
        "打开",
        "闭合",
    ]
    template_invariants = [
        '"Skill Design"',
        '"Ai Studio"',
        "一条小腿",
        "完整角色",
        "全部四张参考图",
        "毛毡",
        "布料",
        "描边",
        "角色专属装饰",
        "标题外轮廓色",
        "标题内描边色",
        "不复制其具体描边色相",
    ]
    rubric_invariants = [
        "硬门槛",
        "五张内置动作版参考图",
        "不是纯提示词",
        "重新生成",
        "18/20",
        "连续外轮廓",
        "内侧立体绳线",
        "不得固定套用样片",
    ]

    for value in skill_invariants:
        if value not in skill:
            errors.append(f"SKILL.md does not preserve invariant: {value}")
    for value in template_invariants:
        if value not in template:
            errors.append(f"prompt template does not preserve invariant: {value}")
    for value in rubric_invariants:
        if value not in rubric:
            errors.append(f"rubric does not preserve invariant: {value}")

    for relative in required_files:
        if relative.endswith(".png"):
            try:
                size = png_size(ROOT / relative)
            except ValueError as exc:
                errors.append(f"{relative}: {exc}")
                continue
            if size != (1086, 1448):
                errors.append(f"{relative}: expected 1086x1448, got {size[0]}x{size[1]}")

if errors:
    for error in errors:
        print(f"[FAIL] {error}")
    raise SystemExit(1)

print("[OK] skill structure, eight 3:4 reference images, dependency chain, layout locks, material locks, and acceptance gates are present")
