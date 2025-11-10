from pathlib import Path
from modules.ingest import Document
from modules.parse_md import MarkdownParser


def test_parse_sections_headings(tmp_path: Path):
    content = "# Título\n\nTexto.\n\n## Sub\nMais texto."
    doc = Document(path=tmp_path / "a.md", text=content, encoding="utf-8")
    parser = MarkdownParser()
    parsed = parser.parse(doc)
    assert len(parsed.sections) >= 2
    assert parsed.sections[0].title == "Título"
    assert "Texto." in parsed.sections[0].content
