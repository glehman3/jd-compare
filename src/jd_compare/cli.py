from __future__ import annotations

import argparse
import json
import sys

from .compare import compare_markdown, compare_postings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare two job postings.")
    parser.add_argument("file_a")
    parser.add_argument("file_b")
    parser.add_argument("--format", choices=("md", "json"), default="md")
    args = parser.parse_args(argv)

    try:
        text_a = open(args.file_a, encoding="utf-8").read()
        text_b = open(args.file_b, encoding="utf-8").read()
        data = compare_postings(text_a, text_b)
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(compare_markdown(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
