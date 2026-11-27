# Templates

Três templates embutidos (`templates/`), selecionados com `-t/--template`:

| Nome | Arquivo | Quando usar |
|---|---|---|
| `formal` (padrão) | `formal.docx` | Incidentes, comunicados e manuais oficiais: metadados, resumo executivo, responsáveis e aprovação |
| `leve` | `leve.docx` | How-tos, regras e referências do dia a dia — cabe em 1 página |

Qualquer `.docx` próprio também funciona: o gerador preserva cabeçalho,
rodapé e estilos dele e reconstrói só o corpo. Estilos reconhecidos (com
degradação graciosa quando ausentes): `Heading 1/2/3`, `Normal`, `List Bullet`,
`List Number`, `Table Grid`, `Intense Quote`.

## Regenerar os embutidos

`formal.docx` e `leve.docx` são gerados por `scripts/build_templates.py`
(espelham os PDFs de referência) — nunca edite o binário à mão:

```bash
uv run python scripts/build_templates.py
```
