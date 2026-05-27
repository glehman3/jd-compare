"""Deterministic posting smell flags."""
from __future__ import annotations

import re

_BUZZWORDS = re.compile(
    r"(?i)\b(rockstar|ninja|guru|wizard|wear many hats|hit the ground running)\b"
)
_SALARY = re.compile(r"(?i)\b(salary|compensation|\$\d|pay range)\b")
_DUPLICATE_LINE: dict[str, int] = {}


def posting_flags(posting: str) -> list[dict[str, str]]:
    flags: list[dict[str, str]] = []
    lines = [ln.strip() for ln in posting.splitlines() if ln.strip()]
    bullets = [ln for ln in lines if ln.startswith(("-", "•", "*")) or re.match(r"^\d+\.", ln)]

    if len(bullets) >= 35:
        flags.append({
            "code": "laundry_list",
            "severity": "info",
            "message": f"Posting has {len(bullets)} bullet-like lines — may be hard to tailor precisely.",
        })

    if len(posting) > 12000:
        flags.append({
            "code": "very_long",
            "severity": "info",
            "message": "Posting exceeds ~12k characters — consider trimming before analysis.",
        })

    if not _SALARY.search(posting):
        flags.append({
            "code": "no_comp_hint",
            "severity": "info",
            "message": "No obvious salary or compensation mention.",
        })

    if _BUZZWORDS.search(posting):
        flags.append({
            "code": "buzzwords",
            "severity": "warn",
            "message": "Contains hype terms (rockstar/ninja/etc.) — read responsibilities carefully.",
        })

    seen: dict[str, int] = {}
    for ln in lines:
        key = re.sub(r"\s+", " ", ln.lower())[:120]
        if len(key) > 20:
            seen[key] = seen.get(key, 0) + 1
    dupes = [k for k, v in seen.items() if v > 1]
    if dupes:
        flags.append({
            "code": "duplicate_lines",
            "severity": "warn",
            "message": f"Found {len(dupes)} repeated line(s) — possible copy-paste boilerplate.",
        })

    if "years of experience" in posting.lower() and posting.lower().count("years") >= 4:
        flags.append({
            "code": "experience_noise",
            "severity": "info",
            "message": "Multiple experience-year requirements — verify which are hard requirements.",
        })

    qual = re.search(r"(?im)^(requirements?|qualifications?)\s*:?\s*$", posting)
    if not qual and len(posting) > 500:
        flags.append({
            "code": "no_qual_section",
            "severity": "info",
            "message": "No clear Requirements/Qualifications header — keywords may land in general bucket.",
        })

    return flags
