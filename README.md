# doc-relatorio

Generate styled DOCX documents from Markdown using a template: formal reports,
light how-tos, or any custom `.docx`. The generator preserves the template's
header, footer and styles and rebuilds only the body — no anchor-text coupling,
so it works with any template.

## Templates

| Name | File | Use for |
|---|---|---|
| `formal` (default) | `templates/formal.docx` | Incidents, announcements, official manuals |
| `leve` | `templates/leve.docx` | How-tos and day-to-day references (1 page) |

Details in [`docs/TEMPLATES.md`](docs/TEMPLATES.md). Templates are generated
by `scripts/build_templates.py` — never edit the binaries by hand.

## Quickstart

```bash
uv sync

# validate only
uv run docxforge exemplos/guia-leve.md --check

# generate (default: formal template, output next to the MD)
uv run docxforge exemplos/incidente-formal.md -t formal
uv run docxforge exemplos/guia-leve.md -t leve -o guia.docx

# any custom template also works
uv run docxforge doc.md -t meu-template.docx

uv run docxforge --list-templates
```

## Markdown syntax

| Syntax | DOCX output |
|---|---|
| `# Title` | New section (Heading 1) |
| `## Sub` / `### Sub` | Sub-heading (Heading 2/3) |
| `**Label:** value` | Bold label + value in the same paragraph |
| `**Label:**` (no value) | Bold-only paragraph |
| Plain text | Justified paragraph (inline `**bold**` supported) |
| `- item` | Bulleted list item |
| `1. item` | Numbered list item |
| `> quote` | Indented italic quote |
| `\| a \| b \|` + separator row | Table (header + rows) |
| `![caption](path.png)` | Centered image (path relative to the MD file) |
| `...` or `---` | Empty spacer paragraph |

## Project layout

```
docxforge/
├── pyproject.toml          # deps + docxforge entry point
├── docxforge/
│   ├── modelos.py          # document data model
│   ├── parser_md.py        # Markdown -> model
│   ├── renderizador.py     # model -> DOCX (style-based)
│   ├── templates.py        # built-in template registry
│   └── cli.py              # CLI
├── scripts/
│   └── build_templates.py  # generates templates/*.docx
├── templates/              # formal.docx, leve.docx (generated, see scripts/)
├── exemplos/               # incidente-formal.md, guia-leve.md (fictitious, generic)
├── docs/TEMPLATES.md       # template guide
└── tests/                  # pytest suite
```

## Development

```bash
uv sync
uv run pytest -q
uv run ruff check . && uv run ruff format --check .
uv run python scripts/build_templates.py   # regenerate templates
```

Conventions for agents: [`AGENTS.md`](AGENTS.md).
