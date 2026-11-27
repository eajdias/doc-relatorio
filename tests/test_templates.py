"""Template registry + generated template sanity tests."""

from docx import Document

from docxforge import templates


def test_embutidos_resolvem():
    nomes = set(templates.listar())
    assert {"formal", "leve"} <= nomes
    assert templates.resolver(None).name == "formal.docx"
    assert templates.resolver("leve").name == "leve.docx"


def test_templates_tem_estilos_e_estrutura():
    for nome in ("formal", "leve"):
        doc = Document(str(templates.resolver(nome)))
        estilos = {s.name for s in doc.styles}
        assert {"Heading 1", "Normal", "List Bullet", "List Number", "Table Grid"} <= estilos
        assert len(doc.tables) >= 2  # meta + conteúdo
        assert "EMPRESA" in doc.sections[0].header.paragraphs[0].text
