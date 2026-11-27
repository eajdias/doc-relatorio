"""Renderização do modelo para DOCX usando os estilos do template.

O gerador preserva cabeçalho, rodapé, estilos e numeração do template e
reconstrói o corpo a partir do modelo — sem depender de textos-âncora dentro
do template. Funciona com qualquer DOCX (formal, leve ou próprio).

Quando o template não tem um estilo, o renderizador degrada com graça: marcadores/números viram prefixo
de texto e cabeçalhos viram parágrafo em negrito.
"""

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

_RE_NEGRITO = re.compile(r"\*\*(.+?)\*\*")


class Renderizador:
    """Gera um DOCX a partir de um Relatorio usando um arquivo DOCX como template."""

    def __init__(self, template: str | Path, base_dir: str | Path | None = None) -> None:
        self.doc = Document(str(template))
        self.base_dir = Path(base_dir) if base_dir else None
        self._estilos = {s.name for s in self.doc.styles}
        self._num = 0  # contador de lista ordenada (reseta fora de sequência)
        self._limpar_corpo()

    # -- estilos ----------------------------------------------------------

    def _estilo(self, *candidatos: str) -> str | None:
        for nome in candidatos:
            if nome in self._estilos:
                return nome
        return None

    def _limpar_corpo(self) -> None:
        from docx.oxml.ns import qn

        body = self.doc.element.body
        for child in list(body):
            if child.tag != qn("w:sectPr"):
                body.remove(child)

    # -- primitivas -------------------------------------------------------

    def _runs_negrito(self, paragrafo, texto: str) -> None:
        """Adiciona runs respeitando `**negrito**` inline no texto."""
        pos = 0
        for m in _RE_NEGRITO.finditer(texto):
            if m.start() > pos:
                paragrafo.add_run(texto[pos : m.start()])
            paragrafo.add_run(m.group(1)).bold = True
            pos = m.end()
        if pos < len(texto):
            paragrafo.add_run(texto[pos:])

    def _paragrafo(
        self,
        texto: str,
        estilo: str | None = None,
        negrito: bool = False,
        italico: bool = False,
        tamanho: Pt | None = None,
        alinhar: WD_ALIGN_PARAGRAPH | None = None,
    ):
        p = self.doc.add_paragraph(style=estilo) if estilo else self.doc.add_paragraph()
        if alinhar is not None:
            p.alignment = alinhar
        if "**" in texto and not (negrito and texto.startswith("**")):
            self._runs_negrito(p, texto)
        else:
            run = p.add_run(texto)
            run.bold = negrito or None
            run.italic = italico or None
            if tamanho is not None:
                run.font.size = tamanho
        return p

    # -- blocos -----------------------------------------------------------

    def _secao(self, titulo: str) -> None:
        estilo = self._estilo("Heading 1", "Título 1", "Title")
        if estilo:
            p = self.doc.add_paragraph(titulo, style=estilo)
            p.alignment = None
        else:
            self._paragrafo(titulo, negrito=True, tamanho=Pt(16))

    def _cabecalho(self, texto: str, nivel: int) -> None:
        estilo = self._estilo(f"Heading {nivel}", f"Título {nivel}")
        if estilo:
            self.doc.add_paragraph(texto, style=estilo)
        else:
            self._paragrafo(texto, negrito=True, tamanho=Pt(14 if nivel == 2 else 12))

    def _corpo(self, texto: str) -> None:
        estilo = self._estilo("normal", "Normal")
        p = self._paragrafo(texto, estilo=estilo)
        if p.alignment is None:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def _rotulo_valor(self, label: str, value: str) -> None:
        estilo = self._estilo("normal", "Normal")
        p = self.doc.add_paragraph(style=estilo) if estilo else self.doc.add_paragraph()
        p.add_run(label).bold = True
        valor = value.replace("\\n", "\n")
        linhas = valor.split("\n")
        primeiro = linhas[0].strip()
        if primeiro:
            p.add_run(" " + primeiro)
        for extra in linhas[1:]:
            p.add_run().add_break()
            if extra.strip():
                p.add_run("\t" + extra.strip())

    def _item(self, texto: str, ordenado: bool) -> None:
        if ordenado:
            estilo = self._estilo("List Number", "Lista Numerada")
            if estilo:
                self._num = 0
                self._paragrafo(texto, estilo=estilo)
            else:
                self._num += 1
                self._corpo(f"{self._num}. {texto}")
        else:
            self._num = 0
            estilo = self._estilo("List Bullet", "Lista com Marcadores")
            if estilo:
                self._paragrafo(texto, estilo=estilo)
            else:
                self._corpo(f"• {texto}")

    def _citacao(self, texto: str) -> None:
        estilo = self._estilo("Intense Quote", "Citação Intensa", "Quote", "Citação")
        p = self._paragrafo(texto, estilo=estilo, italico=estilo is None)
        p.paragraph_format.left_indent = Cm(1)

    def _tabela(self, tabela) -> None:
        larguras = [len(tabela.cabecalho)] + [len(l) for l in tabela.linhas]
        ncols = max(larguras) if larguras else 0
        if ncols == 0:
            return
        estilo = self._estilo("Table Grid", "Tabela com Grade")
        tbl = self.doc.add_table(rows=1 + len(tabela.linhas), cols=ncols)
        if estilo:
            tbl.style = estilo
        for j in range(ncols):
            cel = tbl.cell(0, j)
            cel.text = ""
            if j < len(tabela.cabecalho):
                run = cel.paragraphs[0].add_run(tabela.cabecalho[j])
                run.bold = True
        for i, linha in enumerate(tabela.linhas, start=1):
            for j in range(ncols):
                if j < len(linha):
                    tbl.cell(i, j).text = ""
                    self._runs_negrito(tbl.cell(i, j).paragraphs[0], linha[j])

    def _imagem(self, caminho: str, legenda: str) -> None:
        base = self.base_dir or Path.cwd()
        arquivo = Path(caminho)
        if not arquivo.is_absolute():
            arquivo = base / arquivo
        if not arquivo.exists():
            raise FileNotFoundError(f"Imagem não encontrada: {caminho}")
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(arquivo), width=Cm(14))
        if legenda:
            cap = self.doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = cap.add_run(legenda)
            run.italic = True

    def _limpar_nao_usados(self) -> None:
        """Remove imagens do template que ficaram sem referência no corpo."""
        from docx.opc.constants import RELATIONSHIP_TYPE

        xml = self.doc.element.xml
        part = self.doc.part
        for rId, rel in list(part.rels.items()):
            if rel.reltype != RELATIONSHIP_TYPE.IMAGE:
                continue
            if f'"{rId}"' not in xml:
                part.drop_rel(rId)

    # -- entrada ----------------------------------------------------------

    def render(self, relatorio) -> None:
        from docxforge.modelos import (
            Cabecalho,
            Citacao,
            Espaco,
            Imagem,
            Item,
            LabelValue,
            Paragrafo,
            Tabela,
            TituloNegrito,
        )

        for secao in relatorio.secoes:
            self._secao(secao.titulo.strip())
            for bloco in secao.blocos:
                if isinstance(bloco, LabelValue):
                    self._rotulo_valor(bloco.label, bloco.value)
                elif isinstance(bloco, Paragrafo):
                    self._num = 0
                    self._corpo(bloco.texto)
                elif isinstance(bloco, Citacao):
                    self._num = 0
                    self._citacao(bloco.texto)
                elif isinstance(bloco, TituloNegrito):
                    self._num = 0
                    self._paragrafo(
                        bloco.texto,
                        estilo=self._estilo("normal", "Normal"),
                        negrito=True,
                    )
                elif isinstance(bloco, Cabecalho):
                    self._num = 0
                    self._cabecalho(bloco.texto, bloco.nivel)
                elif isinstance(bloco, Item):
                    self._item(bloco.texto, bloco.ordenado)
                elif isinstance(bloco, Espaco):
                    self._num = 0
                    self.doc.add_paragraph()
                elif isinstance(bloco, Imagem):
                    self._num = 0
                    self._imagem(bloco.caminho, bloco.legenda)
                elif isinstance(bloco, Tabela):
                    self._num = 0
                    self._tabela(bloco)

    def salvar(self, destino: str | Path) -> None:
        self._limpar_nao_usados()
        self.doc.save(str(destino))


def gerar(
    template: str | Path,
    relatorio,
    destino: str | Path,
    base_dir: str | Path | None = None,
) -> None:
    """Gera um DOCX a partir do modelo usando o template."""
    render = Renderizador(template, base_dir=base_dir)
    render.render(relatorio)
    render.salvar(destino)
