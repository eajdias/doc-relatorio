"""Gera os templates DOCX embutidos (`templates/formal.docx`, `templates/leve.docx`).

Os templates são código — não binários opacos: rode este script para
regenerá-los após qualquer ajuste. O conteúdo-esqueleto replica os PDFs de
referência em `Downloads/` (Documento formal / Documento leve).

Uso:
    uv run python scripts/build_templates.py
"""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RAIZ = Path(__file__).resolve().parent.parent
DIR_SAIDA = RAIZ / "templates"

AZUL = RGBColor(0x1F, 0x4E, 0x79)
CINZA = RGBColor(0x59, 0x59, 0x59)


def _base(titulo_header: str) -> Document:
    doc = Document()
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2.2)
        section.bottom_margin = Cm(2.2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
    header = doc.sections[0].header
    header.is_linked_to_previous = False
    p = header.paragraphs[0]
    run = p.add_run(titulo_header)
    run.bold = True
    run.font.size = Pt(9)
    run.font.color.rgb = CINZA
    footer = doc.sections[0].footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("GERAL • EMPRESA • TEMPLATE • PÁGINA ")
    run.font.size = Pt(9)
    run.font.color.rgb = CINZA
    run = p.add_run()
    _page_field(run)
    for r in p.runs:
        r.font.size = Pt(9)
        r.font.color.rgb = CINZA
    return doc


def _page_field(run) -> None:
    inicio = OxmlElement("w:fldChar")
    inicio.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fim = OxmlElement("w:fldChar")
    fim.set(qn("w:fldCharType"), "end")
    run._r.append(inicio)
    run._r.append(instr)
    run._r.append(fim)


def _titulo(doc: Document, texto: str) -> None:
    p = doc.add_paragraph(texto, style="Title")
    for run in p.runs:
        run.font.color.rgb = AZUL


def _guia(doc: Document, texto: str):
    p = doc.add_paragraph(style="Normal")
    run = p.add_run(texto)
    run.italic = True
    run.font.color.rgb = CINZA
    return p


def _meta(doc: Document, linhas: list[tuple[str, str]]) -> None:
    tbl = doc.add_table(rows=1 + len(linhas), cols=2)
    tbl.style = "Table Grid"
    hdr = tbl.rows[0].cells
    hdr[0].paragraphs[0].add_run("CAMPO").bold = True
    hdr[1].paragraphs[0].add_run("INFORMAÇÃO").bold = True
    for i, (campo, valor) in enumerate(linhas, start=1):
        tbl.rows[i].cells[0].paragraphs[0].add_run(campo).bold = True
        tbl.rows[i].cells[1].paragraphs[0].add_run(valor)


def _tabela_generica(doc: Document, colunas: list[str], exemplo: list[str]) -> None:
    tbl = doc.add_table(rows=2, cols=len(colunas))
    tbl.style = "Table Grid"
    for j, col in enumerate(colunas):
        tbl.rows[0].cells[j].paragraphs[0].add_run(col).bold = True
    for j, val in enumerate(exemplo):
        tbl.rows[1].cells[j].paragraphs[0].add_run(val)


def formal() -> Document:
    doc = _base("EMPRESA | TEMPLATE — Documento formal")
    _titulo(doc, "TEMPLATE - Documento formal")
    _guia(
        doc,
        "Como usar: incidentes, comunicados e manuais oficiais. Preencha e apague as orientações.",
    )
    _meta(
        doc,
        [
            ("Documento", "[PREENCHER]"),
            ("Data desta versão", "[PREENCHER]"),
            ("Versão", "[PREENCHER]"),
            ("Status", "[PREENCHER]"),
            ("Classificação", "[PREENCHER]"),
        ],
    )
    doc.add_heading("OBJETIVO DO DOCUMENTO", level=1)
    _guia(doc, "[PREENCHER]")
    doc.add_heading("Resumo executivo", level=1)
    _guia(doc, "[PREENCHER]")
    doc.add_heading("1. [Seção numerada]", level=1)
    _guia(
        doc,
        "[PREENCHER: tabelas CAMPO/AVALIAÇÃO para dados; separe fato, declaração e hipótese.]",
    )
    doc.add_heading("Responsáveis e validação", level=1)
    _tabela_generica(doc, ["NOME", "FUNÇÃO", "PARTICIPAÇÃO"], ["[PREENCHER]"] * 3)
    doc.add_heading("Aprovação", level=1)
    _tabela_generica(doc, ["VALIDAÇÃO", "RESPONSÁVEL", "DATA"], ["[PREENCHER]"] * 3)
    return doc


def leve() -> Document:
    doc = _base("EMPRESA | TEMPLATE — Documento leve")
    _titulo(doc, "TEMPLATE - Documento leve")
    _guia(
        doc,
        "Como usar: duplique este documento, preencha cada bloco e apague as orientações em itálico. "
        "Documentos leves servem para how-tos, regras e referências do dia a dia — cabem em 1 página.",
    )
    _meta(
        doc,
        [
            ("Departamento", "[PREENCHER: ex. SAC]"),
            ("Responsável", "[PREENCHER: time ou pessoa]"),
            ("Revisado em", "[PREENCHER: AAAA-MM]"),
            ("Vale para", "[PREENCHER: situação em que este doc se aplica]"),
            ("Versão", "1.0"),
        ],
    )
    doc.add_heading("OBJETIVO DO DOCUMENTO", level=1)
    _guia(doc, "[PREENCHER: 1 a 2 frases — o que o leitor consegue fazer depois de ler.]")
    doc.add_heading("Passo a passo / Regras", level=1)
    _guia(
        doc,
        "[PREENCHER: numerado para sequência, bullets para regras. Cada item: 1 ação verificável.]",
    )
    doc.add_paragraph("[PREENCHER: item 1]", style="List Number")
    doc.add_paragraph("[PREENCHER: item 2]", style="List Number")
    doc.add_heading("Exemplo de tabela (apague se não usar)", level=1)
    _tabela_generica(doc, ["COLUNA A", "COLUNA B"], ["[PREENCHER]"] * 2)
    doc.add_heading("Como verificar", level=1)
    _guia(doc, "[PREENCHER: obrigatório — como o leitor confirma que deu certo.]")
    doc.add_heading("Regras do padrão", level=1)
    for regra in [
        "Títulos sem emoji; sem formatação fora de títulos, negrito, listas e tabelas.",
        "Dados comparáveis sempre em tabela, nunca só em parágrafo.",
        "Nunca escreva senhas, tokens, chaves ou credenciais.",
        "Curto: cabe em 1 página; se passar, divida em dois documentos.",
    ]:
        doc.add_paragraph(regra, style="List Bullet")
    return doc


def main() -> None:
    DIR_SAIDA.mkdir(exist_ok=True)
    for nome, builder in (("formal.docx", formal), ("leve.docx", leve)):
        destino = DIR_SAIDA / nome
        builder().save(str(destino))
        print(f"Template gerado: {destino}")


if __name__ == "__main__":
    main()
