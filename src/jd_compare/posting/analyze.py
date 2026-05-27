from __future__ import annotations

from .rubric import extract_job_keywords, extract_posting_title, keywords_for_block, split_posting_sections


def analyze_posting(posting: str) -> dict:
    sections = split_posting_sections(posting)
    return {
        "title": extract_posting_title(posting),
        "keywords": extract_job_keywords(posting),
        "required_keywords": keywords_for_block(sections["required"], 20),
        "preferred_keywords": keywords_for_block(sections["preferred"], 15),
    }
