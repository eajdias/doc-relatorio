"""Ponto de entrada da linha de comando do gerador de documentos."""

import argparse
from pathlib import Path

from docxforge import templates
from docxforge.parser_md import parse_md
from docxforge.renderizador import gerar


def _resumir(relatorio) -> str:
    from docxforge.modelos import Imagem, Tabela

    n_blocos = sum(len(s.blocos) for s in relatorio.secoes)
    n_tabelas = sum(isinstance(b, Tabela) for s in relatorio.secoes for b in s.blocos)
    n_imagens = sum(isinstance(b, Imagem) for s in relatorio.secoes for b in s.blocos)
    return (
        f"{len(relatorio.secoes)} seções, {n_blocos} blocos, "
        f"{n_tabelas} tabelas, {n_imagens} imagens"
    )


def _main() -> None:
    ap = argparse.ArgumentParser(
        description="Gera um documento DOCX a partir de Markdown usando um template.",
    )
    ap.add_argument("md", nargs="?", help="Arquivo Markdown de entrada")
    ap.add_argument(
        "-o",
        "--output",
        help="Arquivo DOCX de saída (padrão: mesmo nome do MD com extensão .docx)",
    )
    ap.add_argument(
        "-t",
        "--template",
        default=templates.PADRAO,
        help=f"Template: nome embutido ou caminho .docx (padrão: {templates.PADRAO})",
    )
    ap.add_argument(
        "--list-templates",
        action="store_true",
        help="Lista os templates embutidos disponíveis e sai",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="Só valida o Markdown (não gera DOCX)",
    )
    args = ap.parse_args()

    if args.list_templates:
        for nome, caminho in sorted(templates.listar().items()):
            print(f"{nome}: {caminho.name}")
        return

    if not args.md:
        ap.error("informe o arquivo Markdown (ou use --list-templates)")
    md = Path(args.md)
    if not md.exists():
        ap.error(f"Arquivo não encontrado: {md}")
    try:
        template = templates.resolver(args.template)
    except FileNotFoundError as e:
        ap.error(str(e))

    relatorio = parse_md(md)
    if not relatorio.secoes:
        ap.error("Markdown vazio ou sem conteúdo reconhecível")

    if args.check:
        print(f"OK: {md} → {_resumir(relatorio)} (template: {template.name})")
        return

    destino = Path(args.output) if args.output else md.with_suffix(".docx")
    try:
        gerar(template, relatorio, destino, base_dir=md.parent)
    except FileNotFoundError as e:
        ap.error(str(e))
    print(f"Documento gerado: {destino} (template: {template.name})")


if __name__ == "__main__":
    _main()
