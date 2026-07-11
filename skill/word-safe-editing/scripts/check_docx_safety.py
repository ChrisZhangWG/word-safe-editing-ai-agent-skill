#!/usr/bin/env python3
"""Safety checks for existing DOCX edits.

This is a structural gate, not a visual QA replacement. Use it before Word-open,
Word-save, and render checks. The script intentionally uses only the Python
standard library so it can run in Codex, Terminal, or a clean macOS environment.
"""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def q(ns: str, name: str) -> str:
    return f"{{{ns}}}{name}"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if tag.startswith("{") else tag


@dataclass
class Issue:
    severity: str
    code: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run safety checks on DOCX files.")
    parser.add_argument("docx", nargs="+", type=Path)
    parser.add_argument("--must-contain", action="append", default=[])
    parser.add_argument("--must-not-contain", action="append", default=[])
    parser.add_argument("--expect-text-count", action="append", default=[], metavar="TEXT=N")
    parser.add_argument("--forbid-images-between", nargs=2, metavar=("START", "END"))
    parser.add_argument("--forbid-figure-captions-between", nargs=2, metavar=("START", "END"))
    parser.add_argument("--max-row-height-between", nargs=3, metavar=("START", "END", "DXA"))
    parser.add_argument("--warn-unreferenced-media", action="store_true")
    parser.add_argument("--fail-on-warnings", action="store_true")
    return parser.parse_args()


def read_xml(zf: zipfile.ZipFile, name: str) -> ET.Element:
    return ET.fromstring(zf.read(name))


def text_nodes(el: ET.Element) -> list[str]:
    return [node.text or "" for node in el.iter(q(W, "t"))]


def body_text(root: ET.Element) -> str:
    lines = []
    for p in root.iter(q(W, "p")):
        text = "".join(text_nodes(p)).strip()
        if text:
            lines.append(text)
    return "\n".join(lines)


def element_text(el: ET.Element) -> str:
    return "".join(text_nodes(el)).strip()


def iter_between_body_children(root: ET.Element, start: str, end: str):
    body = root.find(q(W, "body"))
    if body is None:
        return
    active = False
    for child in list(body):
        text = element_text(child)
        if text == start:
            active = True
            continue
        if active and text == end:
            break
        if active:
            yield child


def rel_source_base(rels_name: str) -> str:
    parts = rels_name.split("/")
    if rels_name == "_rels/.rels":
        return ""
    if "_rels" not in parts:
        return posixpath.dirname(rels_name)
    idx = parts.index("_rels")
    return "/".join(parts[:idx])


def resolve_target(base: str, target: str) -> str:
    if target.startswith("/"):
        return posixpath.normpath(target.lstrip("/"))
    return posixpath.normpath(posixpath.join(base, target))


def check_rels(zf: zipfile.ZipFile, names: set[str], issues: list[Issue]) -> set[str]:
    referenced = set()
    for rels_name in sorted(n for n in names if n.endswith(".rels")):
        try:
            root = read_xml(zf, rels_name)
        except Exception as exc:
            issues.append(Issue("error", "invalid-rels-xml", f"{rels_name}: {exc}"))
            continue
        base = rel_source_base(rels_name)
        for rel in root.findall(q(REL, "Relationship")):
            target = rel.get("Target")
            if not target or rel.get("TargetMode") == "External":
                continue
            resolved = resolve_target(base, target)
            referenced.add(resolved)
            if resolved not in names:
                issues.append(Issue("error", "missing-relationship-target", f"{rels_name} -> {target} missing {resolved}"))
    return referenced


def root_start_tag(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="ignore")
    match = re.search(r"<[^!?][^>]*>", text)
    return match.group(0) if match else ""


def check_mc_ignorable(name: str, raw: bytes, root: ET.Element, issues: list[Issue]) -> None:
    ignorable = root.get(q(MC, "Ignorable"))
    if not ignorable:
        return
    start_tag = root_start_tag(raw)
    for prefix in ignorable.split():
        if f"xmlns:{prefix}=" not in start_tag:
            issues.append(Issue("error", "missing-mc-namespace", f"{name}: mc:Ignorable references undeclared prefix {prefix!r}"))


def check_all_xml(zf: zipfile.ZipFile, names: set[str], issues: list[Issue]) -> dict[str, ET.Element]:
    roots = {}
    for name in sorted(n for n in names if n.endswith(".xml")):
        raw = zf.read(name)
        try:
            root = ET.fromstring(raw)
            roots[name] = root
        except Exception as exc:
            issues.append(Issue("error", "invalid-xml", f"{name}: {exc}"))
            continue
        check_mc_ignorable(name, raw, root, issues)
    return roots


def check_word_field_structure(root: ET.Element, issues: list[Issue]) -> None:
    for p in root.iter(q(W, "p")):
        for child in list(p):
            if child.tag in {q(W, "fldChar"), q(W, "instrText")}:
                issues.append(Issue("error", "field-not-in-run", f"{local_name(child.tag)} appears directly under w:p"))


def check_duplicate_drawing_ids(root: ET.Element, issues: list[Issue]) -> None:
    seen = set()
    for el in root.iter():
        if local_name(el.tag) != "docPr":
            continue
        did = el.get("id")
        if not did:
            continue
        if did in seen:
            issues.append(Issue("warning", "duplicate-drawing-id", f"drawing docPr id {did} appears more than once"))
        seen.add(did)


def count_media_nodes(el: ET.Element) -> int:
    return sum(1 for node in el.iter() if node.tag in {q(W, "drawing"), q(W, "pict"), q(W, "object")})


def check_text_expectations(text: str, args: argparse.Namespace, issues: list[Issue]) -> None:
    for needle in args.must_contain:
        if needle not in text:
            issues.append(Issue("error", "missing-required-text", repr(needle)))
    for needle in args.must_not_contain:
        if needle in text:
            issues.append(Issue("error", "forbidden-text", repr(needle)))
    for spec in args.expect_text_count:
        if "=" not in spec:
            issues.append(Issue("error", "bad-expect-text-count", spec))
            continue
        needle, expected_s = spec.rsplit("=", 1)
        try:
            expected = int(expected_s)
        except ValueError:
            issues.append(Issue("error", "bad-expect-text-count", spec))
            continue
        actual = text.count(needle)
        if actual != expected:
            issues.append(Issue("error", "unexpected-text-count", f"{needle!r}: expected {expected}, got {actual}"))


def check_forbidden_images_between(root: ET.Element, args: argparse.Namespace, issues: list[Issue]) -> None:
    if args.forbid_images_between:
        start, end = args.forbid_images_between
        count = sum(count_media_nodes(child) for child in iter_between_body_children(root, start, end))
        if count:
            issues.append(Issue("error", "forbidden-images-in-section", f"{count} image/object nodes between {start!r} and {end!r}"))
    if args.forbid_figure_captions_between:
        start, end = args.forbid_figure_captions_between
        captions = []
        for child in iter_between_body_children(root, start, end):
            for p in child.iter(q(W, "p")):
                text = element_text(p)
                if text.startswith("Figure "):
                    captions.append(text)
        if captions:
            issues.append(Issue("error", "forbidden-figure-captions-in-section", f"{len(captions)} captions, first={captions[0]!r}"))


def check_row_heights_between(root: ET.Element, args: argparse.Namespace, issues: list[Issue]) -> None:
    if not args.max_row_height_between:
        return
    start, end, threshold_s = args.max_row_height_between
    try:
        threshold = int(threshold_s)
    except ValueError:
        issues.append(Issue("error", "bad-row-height-threshold", threshold_s))
        return
    for child in iter_between_body_children(root, start, end):
        for tr in child.iter(q(W, "tr")):
            h = next(tr.iter(q(W, "trHeight")), None)
            if h is None or h.get(q(W, "val")) is None:
                continue
            try:
                val = int(h.get(q(W, "val")))
            except ValueError:
                continue
            if val > threshold:
                snippet = element_text(tr)[:100]
                issues.append(Issue("error", "oversized-row-height", f"{val} DXA > {threshold} between {start!r}/{end!r}: {snippet!r}"))


def check_docx(path: Path, args: argparse.Namespace) -> list[Issue]:
    issues: list[Issue] = []
    if not path.exists():
        return [Issue("error", "missing-file", str(path))]
    try:
        with zipfile.ZipFile(path) as zf:
            bad = zf.testzip()
            if bad:
                issues.append(Issue("error", "zip-test-failed", bad))
            names = set(zf.namelist())
            roots = check_all_xml(zf, names, issues)
            referenced = check_rels(zf, names, issues)
            media = {n for n in names if n.startswith("word/media/")}
            if args.warn_unreferenced_media:
                for unused in sorted(media - referenced):
                    issues.append(Issue("warning", "unreferenced-media", unused))
            doc = roots.get("word/document.xml")
            if doc is not None:
                text = body_text(doc)
                check_text_expectations(text, args, issues)
                check_word_field_structure(doc, issues)
                check_duplicate_drawing_ids(doc, issues)
                check_forbidden_images_between(doc, args, issues)
                check_row_heights_between(doc, args, issues)
            else:
                issues.append(Issue("error", "missing-document-xml", "word/document.xml"))
    except zipfile.BadZipFile as exc:
        issues.append(Issue("error", "bad-zip", str(exc)))
    return issues


def main() -> int:
    args = parse_args()
    has_error = False
    has_warning = False
    for path in args.docx:
        issues = check_docx(path, args)
        print(f"== {path} ==")
        if not issues:
            print("OK")
            continue
        for issue in issues:
            print(f"{issue.severity.upper()} {issue.code}: {issue.message}")
            has_error = has_error or issue.severity == "error"
            has_warning = has_warning or issue.severity == "warning"
    return 1 if has_error or (args.fail_on_warnings and has_warning) else 0


if __name__ == "__main__":
    sys.exit(main())

