"""Registro dos templates DOCX embutidos e resolução do `-t/--template`.

Um template pode ser:
- o nome de um embutido (`formal`, `leve`);
- um caminho para qualquer arquivo `.docx` (usa cabeçalho, rodapé e estilos dele).
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_TEMPLATES = RAIZ / "templates"

EMBUTIDOS: dict[str, str] = {
    "formal": "formal.docx",
    "leve": "leve.docx",
}

PADRAO = "formal"


def listar() -> dict[str, Path]:
    """Mapeia nome do embutido → caminho do arquivo (só os que existem)."""
    return {
        nome: DIR_TEMPLATES / arquivo
        for nome, arquivo in EMBUTIDOS.items()
        if (DIR_TEMPLATES / arquivo).exists()
    }


def resolver(nome_ou_caminho: str | None) -> Path:
    """Resolve o template a usar; levanta `FileNotFoundError` se não existir."""
    if not nome_ou_caminho:
        nome_ou_caminho = PADRAO
    embutidos = listar()
    if nome_ou_caminho in embutidos:
        return embutidos[nome_ou_caminho]
    caminho = Path(nome_ou_caminho)
    if caminho.exists():
        return caminho
    disponiveis = ", ".join(sorted(embutidos)) or "(nenhum embutido gerado ainda)"
    raise FileNotFoundError(
        f"Template não encontrado: {nome_ou_caminho} "
        f"(embutidos disponíveis: {disponiveis}, ou passe um caminho .docx)"
    )
