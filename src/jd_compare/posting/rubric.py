"""Keyword extraction and posting section parsing."""
from __future__ import annotations

import re

QE_LEXICON = [
    "playwright", "selenium", "test automation", "sdet", "quality engineer",
    "software engineer in test", "api testing", "rest", "ci/cd", "jenkins",
    "github actions", "docker", "kubernetes", "gcp", "aws", "typescript",
    "javascript", "test strategy", "regression", "e2e", "end-to-end",
    "observability", "splunk", "postman", "figma", "testrail", "pytest",
    "quality engineering", "uat", "automation framework", "agile", "scrum",
]

SYNONYM_GROUPS: list[set[str]] = [
    {"playwright", "e2e", "end-to-end", "test automation", "automation framework"},
    {"api testing", "rest", "rest api", "api"},
    {"ci/cd", "jenkins", "github actions", "continuous integration"},
    {"sdet", "software engineer in test", "quality engineer", "qe"},
    {"pytest", "unit testing", "automated testing"},
    {"docker", "kubernetes", "k8s", "container"},
    {"aws", "gcp", "azure", "cloud"},
    {"typescript", "javascript", "node"},
]

_SECTION_REQUIRED = re.compile(
    r"(?im)^(?:requirements?|qualifications?|must[\s-]have|what you(?:'ll| will) bring|"
    r"minimum qualifications|required skills?)\s*:?\s*$"
)
_SECTION_PREFERRED = re.compile(
    r"(?im)^(?:preferred|nice[\s-]to[\s-]have|bonus|pluses?|desired)\s*:?\s*$"
)
_TITLE_HINT = re.compile(
    r"(?im)^(?:position|role|job title|title)\s*:\s*(.+)$|"
    r"^([A-Z][^\n]{8,80}(?:engineer|developer|tester|analyst|manager|specialist)[^\n]{0,40})$"
)
_TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9/+#.\-]{2,}")


def _synonym_lookup() -> dict[str, set[str]]:
    lookup: dict[str, set[str]] = {}
    for group in SYNONYM_GROUPS:
        for term in group:
            lookup[term.lower()] = {t.lower() for t in group if t.lower() != term.lower()}
    return lookup


_SYNONYMS = _synonym_lookup()


def split_posting_sections(posting: str) -> dict[str, str]:
    lines = posting.split("\n")
    required: list[str] = []
    preferred: list[str] = []
    general: list[str] = []
    current = "general"
    for line in lines:
        stripped = line.strip()
        if _SECTION_REQUIRED.match(stripped):
            current = "required"
            continue
        if _SECTION_PREFERRED.match(stripped):
            current = "preferred"
            continue
        if current == "required":
            required.append(line)
        elif current == "preferred":
            preferred.append(line)
        else:
            general.append(line)
    return {
        "required": "\n".join(required).strip(),
        "preferred": "\n".join(preferred).strip(),
        "general": "\n".join(general).strip(),
    }


def extract_job_keywords(posting: str) -> list[str]:
    lower = posting.lower()
    found: list[str] = []
    for term in QE_LEXICON:
        if term in lower and term not in found:
            found.append(term)
    for match in _TOKEN_RE.findall(posting):
        w = match.lower()
        if len(w) >= 4 and w not in found:
            if any(w in q or q in w for q in QE_LEXICON[:15]):
                found.append(w)
    return found[:40]


def extract_posting_title(posting: str) -> str:
    for line in posting.split("\n")[:12]:
        line = line.strip()
        if not line or len(line) > 120:
            continue
        m = _TITLE_HINT.match(line)
        if m:
            return (m.group(1) or m.group(2) or "").strip()
        if re.search(
            r"(?i)\b(engineer|developer|sdet|tester|analyst|manager|specialist)\b",
            line,
        ):
            return line
    first = posting.split("\n", 1)[0].strip()
    return first[:100] if first else ""


def match_term_in_text(term: str, blob: str) -> float:
    t = term.lower().strip()
    if not t:
        return 0.0
    if t in blob:
        return 1.0
    for syn in _SYNONYMS.get(t, ()):
        if syn in blob:
            return 0.75
    return 0.0


def keywords_for_block(text: str, cap: int = 25) -> list[str]:
    if not text.strip():
        return []
    return extract_job_keywords(text)[:cap]
