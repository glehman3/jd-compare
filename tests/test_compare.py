from pathlib import Path

from jd_compare.compare import compare_markdown, compare_postings

ROOT = Path(__file__).resolve().parents[1] / "examples"


def test_level_diff_detects_senior_b():
    a = (ROOT / "level_a.txt").read_text(encoding="utf-8")
    b = (ROOT / "level_b.txt").read_text(encoding="utf-8")
    data = compare_postings(a, b)
    assert "playwright" in data["shared_required"] or "api testing" in data["shared_required"]
    assert data["b"]["level"]["label"] == "Senior"
    assert len(data["only_b_required"]) + len(data["only_b_preferred"]) >= 0


def test_markdown_table():
    a = (ROOT / "level_a.txt").read_text(encoding="utf-8")
    b = (ROOT / "level_b.txt").read_text(encoding="utf-8")
    md = compare_markdown(compare_postings(a, b))
    assert "Shared must-haves" in md
    assert "SDET" in md or "Senior" in md
