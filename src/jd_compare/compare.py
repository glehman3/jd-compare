"""Compare two job postings."""
from __future__ import annotations

import re

from .posting.analyze import analyze_posting
from .posting.flags import posting_flags

_LEVEL_PATTERNS = [
    ("Staff-ish", re.compile(r"(?i)\b(principal|staff|distinguished|architect)\b")),
    ("Senior", re.compile(r"(?i)\b(senior|sr\.?|lead)\b")),
    ("Mid", re.compile(r"(?i)\b(sdet ii|engineer ii|mid[- ]level|3\+?\s*years|4\+?\s*years)\b")),
    ("Junior", re.compile(r"(?i)\b(junior|entry|associate|0-2\s*years|1\+?\s*years)\b")),
]


def infer_level(posting: str, title: str) -> dict:
    blob = f"{title}\n{posting}".lower()
    evidence: list[str] = []
    label = "Mid–Senior (unclear)"
    for name, pattern in _LEVEL_PATTERNS:
        m = pattern.search(blob)
        if m:
            label = name
            evidence.append(f"Matched '{m.group(0)}'")
            break
    for m in re.finditer(r"(\d{1,2})\+?\s*years", posting, re.I):
        evidence.append(f"{m.group(0)} experience mentioned")
    if not evidence:
        evidence.append("No strong seniority markers")
    return {"label": label, "evidence": evidence[:5]}


def _kw_set(items: list[str]) -> set[str]:
    return {x.lower() for x in items}


def compare_postings(text_a: str, text_b: str) -> dict:
    a = analyze_posting(text_a)
    b = analyze_posting(text_b)
    req_a = _kw_set(a["required_keywords"] or a["keywords"])
    req_b = _kw_set(b["required_keywords"] or b["keywords"])
    pref_a = _kw_set(a["preferred_keywords"])
    pref_b = _kw_set(b["preferred_keywords"])
    all_a = req_a | pref_a
    all_b = req_b | pref_b

    return {
        "a": {
            "title": a["title"],
            "level": infer_level(text_a, a["title"] or ""),
            "flags": posting_flags(text_a),
            "required": sorted(req_a),
            "preferred": sorted(pref_a),
        },
        "b": {
            "title": b["title"],
            "level": infer_level(text_b, b["title"] or ""),
            "flags": posting_flags(text_b),
            "required": sorted(req_b),
            "preferred": sorted(pref_b),
        },
        "shared_required": sorted(req_a & req_b),
        "only_a_required": sorted(req_a - req_b),
        "only_b_required": sorted(req_b - req_a),
        "only_a_preferred": sorted(pref_a - pref_b),
        "only_b_preferred": sorted(pref_b - pref_a),
        "shared_any": sorted(all_a & all_b),
        "only_a": sorted(all_a - all_b),
        "only_b": sorted(all_b - all_a),
    }


def compare_markdown(data: dict) -> str:
    lines = [
        "# Job posting comparison",
        "",
        f"| | A | B |",
        f"|---|---|---|",
        f"| **Title** | {data['a']['title'] or '—'} | {data['b']['title'] or '—'} |",
        f"| **Level** | {data['a']['level']['label']} | {data['b']['level']['label']} |",
        "",
        "## Shared must-haves",
        "",
    ]
    for k in data["shared_required"] or ["—"]:
        lines.append(f"- {k}")
    lines.extend(["", "## Only in A (required)", ""])
    for k in data["only_a_required"] or ["—"]:
        lines.append(f"- {k}")
    lines.extend(["", "## Only in B (required)", ""])
    for k in data["only_b_required"] or ["—"]:
        lines.append(f"- {k}")
    lines.extend(["", "## Only in A (preferred)", ""])
    for k in data["only_a_preferred"] or ["—"]:
        lines.append(f"- {k}")
    lines.extend(["", "## Only in B (preferred)", ""])
    for k in data["only_b_preferred"] or ["—"]:
        lines.append(f"- {k}")
    lines.extend(["", "## Posting flags", "", "### A", ""])
    for f in data["a"]["flags"] or [{"message": "None"}]:
        lines.append(f"- {f.get('message', f)}")
    lines.extend(["", "### B", ""])
    for f in data["b"]["flags"] or [{"message": "None"}]:
        lines.append(f"- {f.get('message', f)}")
    return "\n".join(lines)
