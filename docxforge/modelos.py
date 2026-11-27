"""Modelo de dados de um documento (relatório, guia, manual)."""

from dataclasses import dataclass, field


@dataclass
class LabelValue:
    """Parágrafo com rótulo em negrito seguido do valor no mesmo parágrafo."""

    label: str
    value: str


@dataclass
class Paragrafo:
    """Parágrafo de texto justificado."""

    texto: str


@dataclass
class Citacao:
    """Citação recuada (bloco `>` do Markdown)."""

    texto: str


@dataclass
class TituloNegrito:
    """Parágrafo apenas com rótulo em negrito (sem valor)."""

    texto: str


@dataclass
class Cabecalho:
    """Cabeçalho de nível 2 (`##`) ou 3 (`###`) dentro da seção atual."""

    texto: str
    nivel: int = 2


@dataclass
class Item:
    """Item de lista com marcador (`-`) ou numerada (`1.`)."""

    texto: str
    ordenado: bool = False


@dataclass
class Espaco:
    """Parágrafo vazio usado como espaçador (`...` ou `---`)."""


@dataclass
class Imagem:
    """Imagem centralizada (caminho relativo ao arquivo MD)."""

    caminho: str
    legenda: str = ""


@dataclass
class Tabela:
    """Tabela com cabeçalho e linhas."""

    cabecalho: list[str]
    linhas: list[list[str]] = field(default_factory=list)


Bloco = (
    LabelValue | Paragrafo | Citacao | TituloNegrito | Cabecalho | Item | Espaco | Imagem | Tabela
)


@dataclass
class Secao:
    """Seção do documento (cabeçalho nível 1) com seus blocos."""

    titulo: str
    blocos: list[Bloco] = field(default_factory=list)


@dataclass
class Relatorio:
    """Documento completo."""

    secoes: list[Secao] = field(default_factory=list)
