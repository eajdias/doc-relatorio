"""Parser tests: every Markdown construct maps to the right block."""

from pathlib import Path

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
from docxforge.parser_md import parse_md


def _parse(texto: str):
    caminho = Path("/tmp/doc-relatorio-test.md")
    caminho.write_text(texto, encoding="utf-8")
    return parse_md(caminho)


def test_h1_cria_secao_e_h23_viram_cabecalho():
    rel = _parse("# A\n\n## B\n\n### C\n")
    assert [s.titulo for s in rel.secoes] == ["A"]
    assert isinstance(rel.secoes[0].blocos[0], Cabecalho)
    assert rel.secoes[0].blocos[0].nivel == 2
    assert rel.secoes[0].blocos[1].nivel == 3


def test_blocos_antes_do_h1_nao_sao_perdidos():
    rel = _parse("Texto solto.\n\n# A\n")
    assert rel.secoes[0].titulo == "Documento"
    assert isinstance(rel.secoes[0].blocos[0], Paragrafo)


def test_rotulo_valor_e_rotulo_sozinho():
    rel = _parse("# A\n\n**Nome:** Maria\n\n**Sozinho:**\n")
    assert isinstance(rel.secoes[0].blocos[0], LabelValue)
    assert rel.secoes[0].blocos[0].label == "Nome:"
    assert isinstance(rel.secoes[0].blocos[1], TituloNegrito)


def test_listas_numerada_e_com_marcador():
    rel = _parse("# A\n\n1. Um\n2. Dois\n\n- Três\n")
    blocos = rel.secoes[0].blocos
    assert isinstance(blocos[0], Item) and blocos[0].ordenado
    assert isinstance(blocos[2], Item) and not blocos[2].ordenado


def test_citacao_espaco_imagem():
    rel = _parse("# A\n\n> dito\n\n...\n\n---\n\n![leg](a.png)\n")
    blocos = rel.secoes[0].blocos
    assert isinstance(blocos[0], Citacao)
    assert isinstance(blocos[1], Espaco)
    assert isinstance(blocos[2], Espaco)
    assert isinstance(blocos[3], Imagem)
    assert blocos[3].legenda == "leg"


def test_tabela_com_separador():
    rel = _parse("# A\n\n| X | Y |\n| --- | --- |\n| 1 | 2 |\n")
    bloco = rel.secoes[0].blocos[0]
    assert isinstance(bloco, Tabela)
    assert bloco.cabecalho == ["X", "Y"]
    assert bloco.linhas == [["1", "2"]]
