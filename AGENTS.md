# AGENTS.md

```bash
uv sync                              # instala deps + entry point docxforge
uv run docxforge --help        # CLI
uv run docxforge exemplos/guia-leve.md --check   # valida sem gerar
uv run pytest -q                     # testes
uv run ruff check . && uv run ruff format --check .    # lint
uv run python scripts/build_templates.py   # regenera templates/*.docx
```

## Convenções

- Código/comentários/commits em inglês; documentos gerados e exemplos em PT-BR.
- Parser (`docxforge/parser_md.py`): Markdown → modelo (`modelos.py`).
- Renderizador (`docxforge/renderizador.py`): **style-based** — nunca acople a
  textos-âncora do template; use `_estilo()` com fallbacks.
- Templates embutidos vivem como código em `scripts/build_templates.py`.
- Exemplos `incidente-formal.md`/`guia-leve.md` são fictícios e genéricos.
