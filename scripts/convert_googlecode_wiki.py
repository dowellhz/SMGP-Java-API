#!/usr/bin/env python3
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = ROOT / "wiki"

PAGE_TITLES = {
    "ReadMe": "概述",
    "Example": "例子",
    "ClientEvent": "ClientEvent",
    "SimServer": "服务器模拟器",
    "Other": "其他",
    "Downloads": "Downloads",
}

SIDEBAR_ITEMS = [
    ("Home", "首页"),
    ("ReadMe", "概述"),
    ("Example", "例子"),
    ("ClientEvent", "ClientEvent"),
    ("SimServer", "服务器模拟器"),
    ("Other", "其他"),
]


def convert_heading(line):
    match = re.match(r"^(=+)\s*(.*?)\s*\1\s*$", line)
    if not match:
        return None
    level = min(len(match.group(1)), 6)
    return f"{'#' * level} {match.group(2)}"


def convert_links(text):
    def repl(match):
        body = match.group(1).strip()
        parts = body.split(None, 1)
        page = parts[0]
        title = parts[1] if len(parts) > 1 else PAGE_TITLES.get(page, page)
        if page == "Downloads":
            return title
        return f"[[{title}|{page}]]"

    return re.sub(r"\[([A-Za-z0-9_-]+(?:\s+[^\]]+)?)\]", repl, text)


def convert_inline(text):
    text = text.replace("<br/>", "")
    text = convert_links(text)
    return text


def convert_file(source):
    lines = source.read_text(encoding="utf-8").splitlines()
    output = []
    in_code = False

    for line in lines:
        stripped = line.strip()
        if stripped == "{{{":
            output.append("```java")
            in_code = True
            continue
        if stripped == "}}}":
            output.append("```")
            in_code = False
            continue
        if in_code:
            output.append(line)
            continue

        heading = convert_heading(line)
        if heading is not None:
            output.append(heading)
            continue

        if line.startswith("#") and not line.startswith("##"):
            output.append("# " + line[1:].strip())
            continue

        output.append(convert_inline(line))

    result = "\n".join(output).rstrip() + "\n"
    return result


def write_sidebar():
    lines = ["# SMGP API", ""]
    lines.extend(f"- [[{title}|{page}]]" for page, title in SIDEBAR_ITEMS)
    WIKI_DIR.joinpath("_Sidebar.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    for source in sorted(WIKI_DIR.glob("*.wiki")):
        target_name = "Home.md" if source.stem == "Navi" else f"{source.stem}.md"
        WIKI_DIR.joinpath(target_name).write_text(convert_file(source), encoding="utf-8")
    write_sidebar()


if __name__ == "__main__":
    main()
