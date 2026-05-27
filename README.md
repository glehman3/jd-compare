# jd-compare

[![CI](https://github.com/glehman3/jd-compare/actions/workflows/ci.yml/badge.svg)](https://github.com/glehman3/jd-compare/actions/workflows/ci.yml)

Compare **two job postings** side by side — shared must-haves, unique requirements, level signals, and posting flags. Helps recruiters explain req differences to hiring managers.

## Install

```bash
pip install git+https://github.com/glehman3/jd-compare.git
```

## Usage

```bash
jd-compare examples/level_a.txt examples/level_b.txt
jd-compare posting_a.txt posting_b.txt --format json
```

## Output

- Titles and level signals for A vs B
- Shared required keywords
- Only in A / only in B (required and preferred)
- Posting quality flags per file

## Development

```bash
pip install ".[dev]"
pytest -q
```

Patterns adapted from [jd-kit](https://github.com/glehman3/jd-kit); see `ATTRIBUTION.md`.

## License

MIT
