#!/usr/bin/env python3
"""Validate skill-guide HTML reports for stable structure.

This script checks deterministic report rules only. It does not judge content
quality, visual taste, or whether the interpreted skill actually works.
"""

from __future__ import annotations

import re
import sys
from html import unescape
from pathlib import Path


SECTIONS_WITH_EXAMPLES = [
    ("1", "一句话结论"),
    ("2", "快速判断"),
    ("3", "直接开始用"),
    ("4", "和什么技能最搭配"),
    ("5", "产出物示例"),
    ("6", "完整度与改善点"),
    ("7", "适合谁用，不能做什么"),
]

SECTIONS_WITHOUT_EXAMPLES = [
    ("1", "一句话结论"),
    ("2", "快速判断"),
    ("3", "直接开始用"),
    ("4", "和什么技能最搭配"),
    ("5", "完整度与改善点"),
    ("6", "适合谁用，不能做什么"),
]

OLD_MARKERS = [
    "{{",
    "TODO",
    "FIXME",
    "直接试用",
    "搭配使用建议",
    "什么时候适合用",
    "最好能产出什么",
    "产出物对照",
    "试用失败后怎么找我修",
    'class="badge optional"',
    "可选</span>",
    "需安装</span>",
    "不确定</span>",
    ">已有</span>",
    ">未知</span>",
]


def strip_tags(text: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", text)).strip()


def section_html(html: str, number: int) -> str:
    pattern = rf'<section id="sec-{number}">(.*?)(?=<section id="sec-{number + 1}">|<p class="footer">)'
    match = re.search(pattern, html, flags=re.S)
    return match.group(1) if match else ""


def validate(path: Path) -> list[str]:
    html = path.read_text(encoding="utf-8")
    errors: list[str] = []

    for marker in OLD_MARKERS:
        if marker in html:
            errors.append(f"残留旧标记或占位符: {marker}")

    section_ids = re.findall(r'<section id="sec-([1-7])">', html)
    headings = [
        (number, strip_tags(title))
        for number, title in re.findall(r'<section id="sec-([1-7])">\s*<h2>(.*?)</h2>', html, flags=re.S)
    ]
    expected_with = [(number, f"{number}. {title}") for number, title in SECTIONS_WITH_EXAMPLES]
    expected_without = [(number, f"{number}. {title}") for number, title in SECTIONS_WITHOUT_EXAMPLES]

    if headings == expected_with:
        expected_sections = SECTIONS_WITH_EXAMPLES
        usage_section = 7
    elif headings == expected_without:
        expected_sections = SECTIONS_WITHOUT_EXAMPLES
        usage_section = 6
    else:
        expected_sections = SECTIONS_WITH_EXAMPLES
        usage_section = 7
        errors.append(f"章节标题不匹配: {headings}")

    expected_ids = [number for number, _ in expected_sections]
    if section_ids != expected_ids:
        errors.append(f"章节 id 应为 {expected_ids}, 实际为 {section_ids}")

    toc_ids = re.findall(r'<a href="#sec-([1-7])"', html)
    if toc_ids != expected_ids:
        errors.append(f"目录锚点应为 {expected_ids}, 实际为 {toc_ids}")

    sec2 = section_html(html, 2)
    if sec2.count('class="judge-value"') != 5:
        errors.append("快速判断必须有 5 个 judge-value")
    if 'class="span-all"' not in sec2 or "token 消耗预估" not in sec2:
        errors.append("快速判断必须有横跨整行的 token 消耗预估")
    if "改善点" in html:
        for label_html in re.findall(r'<div class="label">改善点.*?</div>', html, flags=re.S):
            if 'class="warn"' in label_html:
                errors.append("普通改善点不应使用 warn 红色,请改用 caution；中等及以上风险应改名为风险点")

    sec3 = section_html(html, 3)
    if 'id="trial-prompt"' not in sec3:
        errors.append("第 3 节缺少第一次试用提示词")
    if "失败了怎么反馈" not in sec3:
        errors.append("第 3 节缺少失败反馈入口")
    if sec3.count('class="copy-block"') < 2:
        errors.append("第 3 节 Pro / Plus 提示词应使用 copy-block")

    sec4 = section_html(html, 4)
    pairing_count = sec4.count('· <span class="badge')
    if pairing_count == 0:
        errors.append("第 4 节缺少搭配对象")
    if "单独用够不够" not in sec4 or "最值得搭配" not in sec4 or "按需搭配" not in sec4:
        errors.append("第 4 节必须包含 单独用够不够 / 最值得搭配 / 按需搭配")
    if "★★★★★" not in sec4 or "★★★" not in sec4:
        errors.append("搭配星级必须放在分组标题里")
    for label in re.findall(r'<span class="badge(?: [^"]+)?">([^<]+)</span>', sec4):
        if label not in {"本机已有", "未安装", "安装状态未知"}:
            errors.append(f"非法搭配状态标签: {label}")
    for line in re.findall(r'·\s*<span class="badge.*?(?:<br>|</div>)', sec4, flags=re.S):
        if 'class="stars"' in line:
            errors.append("单条搭配对象后不应再放 stars,星级只放分组标题")

    if expected_sections == SECTIONS_WITH_EXAMPLES:
        sec5 = section_html(html, 5)
        if 'class="artifact-card"' not in sec5:
            errors.append("产出物示例节必须使用 artifact-card 展示可打开示例")
        if "<table" in sec5:
            errors.append("产出物示例节不应退回输入输出对照表")

    sec7 = section_html(html, usage_section)
    if "包里有什么" not in sec7 or "主流程" not in sec7 or "旁路文件" not in sec7:
        errors.append("最后一节文件关系图必须包含 包里有什么 / 主流程 / 旁路文件")
    skill_cells = sec7.count('class="skill-cell"')
    if skill_cells and "包含哪些 skill" not in sec7:
        errors.append("多 skill 清单必须以“包含哪些 skill”为标题")
    if "包含哪些 skill" in sec7 and skill_cells == 0:
        errors.append("包含哪些 skill 下必须有 skill-cell")
    if "包含哪些 skill" in sec7 and sec7.find("包含哪些 skill") > sec7.find("包里有什么"):
        errors.append("多 skill 场景必须先列技能清单,再写包里有什么")

    return errors


def default_targets() -> list[Path]:
    skill_root = Path(__file__).resolve().parents[1]
    return sorted((skill_root / "examples").glob("*.html"))


def main() -> int:
    targets = [Path(arg) for arg in sys.argv[1:]] or default_targets()
    if not targets:
        print("没有找到要检查的 HTML 文件")
        return 1

    failed = False
    for target in targets:
        errors = validate(target)
        if errors:
            failed = True
            print(f"FAIL {target}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {target}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
