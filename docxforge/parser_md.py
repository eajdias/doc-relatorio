"""Parser de Markdown para o modelo de documento."""

import re
from pathlib import Path

from docxforge.modelos import (
    Bloco,
    Cabecalho,
    Citacao,
    Espaco,
    Imagem,
    Item,
    LabelValue,
    Paragrafo,
    Relatorio,
    Secao,
    Tabela,
    TituloNegrito,
)

_RE_H1 = re.compile(r"^#\s+(.+)$")
_RE_H23 = re.compile(r"^(#{2,3})\s+(.+)$")
_RE_BOLETIM = re.compile(r"^\s*[-*]\s+(.+)$")
_RE_ORDENADO = re.compile(r"^\s*\d+[.)]\s+(.+)$")
_RE_TABELA_LINHA = re.compile(r"^\s*\|")
_RE_TABELA_SEP = re.compile(r"^:?-{3,}:?$")
_RE_IMAGEM = re.compile(r"^!\[(.*?)\]\((.*?)\)\s*$")
_RE_LABEL = re.compile(r"^\*\*(.+?)\*\*\s*(:?)\s*(.*)$")
_RE_ESPACO = re.compile(r"^\s*(\.\.\.|-{3,}|_{3,})\s*$")
_RE_CITACAO = re.compile(r"^\s*>\s?(.*)$")


def _celulas(linha: str) -> list[str]:
    linha = linha.strip()
    linha = linha.removeprefix("|")
    linha = linha.removesuffix("|")
    return [c.strip() for c in linha.split("|")]


def _eh_separador(celulas: list[str]) -> bool:
    return bool(celulas) and all(_RE_TABELA_SEP.match(c.strip()) for c in celulas)


def _label_value(label: str, com_dois_pontos: bool, resto: str) -> Bloco:
    label = label.strip()
    sufixo = ":" if com_dois_pontos else ""
    if resto.strip():
        return LabelValue(label=f"{label}{sufixo}", value=resto)
    return TituloNegrito(texto=f"{label}{sufixo}")


def parse_md(caminho: str | Path) -> Relatorio:
    """Converte um arquivo Markdown em um modelo Relatorio.

    Blocos antes do primeiro `#` caem numa seção implícita "Documento",
    para que arquivos sem título não percam conteúdo em silêncio.
    """
    texto = Path(caminho).read_text(encoding="utf-8")
    relatorio = Relatorio()
    secao_atual: Secao | None = None

    def novo_bloco(bloco: Bloco) -> None:
        nonlocal secao_atual
        if secao_atual is None:
            secao_atual = Secao(titulo="Documento")
            relatorio.secoes.append(secao_atual)
        secao_atual.blocos.append(bloco)

    linhas = texto.splitlines()
    i = 0
    while i < len(linhas):
        linha = linhas[i]

        m = _RE_H1.match(linha)
        if m:
            secao_atual = Secao(titulo=m.group(1).strip())
            relatorio.secoes.append(secao_atual)
            i += 1
            continue

        m = _RE_H23.match(linha)
        if m:
            novo_bloco(Cabecalho(texto=m.group(2).strip(), nivel=len(m.group(1))))
            i += 1
            continue

        if not linha.strip():
            i += 1
            continue

        if _RE_TABELA_LINHA.match(linha):
            bloco_linhas: list[str] = []
            while i < len(linhas) and _RE_TABELA_LINHA.match(linhas[i]):
                bloco_linhas.append(linhas[i])
                i += 1
            tabelas = [_celulas(l) for l in bloco_linhas]
            dados = [t for t in tabelas if not _eh_separador(t)]
            if dados:
                novo_bloco(Tabela(cabecalho=dados[0], linhas=dados[1:]))
            continue

        m = _RE_ORDENADO.match(linha)
        if m:
            novo_bloco(Item(texto=m.group(1).strip(), ordenado=True))
            i += 1
            continue

        m = _RE_BOLETIM.match(linha)
        if m:
            novo_bloco(Item(texto=m.group(1).strip()))
            i += 1
            continue

        m = _RE_IMAGEM.match(linha)
        if m:
            novo_bloco(Imagem(caminho=m.group(2).strip(), legenda=m.group(1).strip()))
            i += 1
            continue

        m = _RE_LABEL.match(linha)
        if m:
            novo_bloco(_label_value(m.group(1), bool(m.group(2)), m.group(3)))
            i += 1
            continue

        m = _RE_CITACAO.match(linha)
        if m:
            novo_bloco(Citacao(texto=m.group(1).strip()))
            i += 1
            continue

        if _RE_ESPACO.match(linha):
            novo_bloco(Espaco())
            i += 1
            continue

        novo_bloco(Paragrafo(texto=linha.strip()))
        i += 1

    return relatorio
