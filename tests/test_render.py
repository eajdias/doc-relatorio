"""Renderer tests: style-based generation on every template, no coupling."""

from pathlib import Path

import pytest
from docx import Document

from docxforge import templates
from docxforge.modelos import Item, LabelValue, Paragrafo, Relatorio, Secao, Tabela
from docxforge.renderizador import gerar

RAIZ = Path(__file__).resolve().parent.parent


def _amostra() -> Relatorio:
    return Relatorio(
        secoes=[
            Secao(
                titulo="Seção um",
                blocos=[
                    LabelValue(label="Campo:", value="valor com **negrito**"),
                    Paragrafo(texto="Texto corrido."),
                    Item(texto="bul", ordenado=False),
                    Item(texto="num", ordenado=True),
                    Tabela(cabecalho=["A", "B"], linhas=[["1", "2"]]),
                ],
            )
        ]
    )


@pytest.mark.parametrize("nome", ["formal", "leve"])
def test_gera_em_todos_os_templates(tmp_path, nome):
    template = templates.resolver(nome)
    destino = tmp_path / f"out-{nome}.docx"
    gerar(template, _amostra(), destino)
    doc = Document(str(destino))
    textos = [p.text for p in doc.paragraphs]
    assert "Seção um" in textos
    assert any("Campo:" in t for t in textos)
    assert len(doc.tables) == 1
    assert not any("PREENCHER" in t for t in textos)


def test_cabecalho_rodape_sobrevivem(tmp_path):
    destino = tmp_path / "out.docx"
    gerar(templates.resolver("formal"), _amostra(), destino)
    doc = Document(str(destino))
    assert "EMPRESA" in doc.sections[0].header.paragraphs[0].text
    assert "PÁGINA" in doc.sections[0].footer.paragraphs[0].text


def test_imagem_inexistente_falha_claro(tmp_path):
    from docxforge.modelos import Imagem as BlocoImagem

    rel = Relatorio(secoes=[Secao(titulo="S", blocos=[BlocoImagem(caminho="nao-existe.png")])])
    with pytest.raises(FileNotFoundError, match="Imagem não encontrada"):
        gerar(templates.resolver("leve"), rel, tmp_path / "out.docx")
