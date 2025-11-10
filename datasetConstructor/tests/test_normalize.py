from pathlib import Path
from modules.ingest import Document
from modules.parse_md import MarkdownParser
from modules.normalize import Normalizer


def test_normalize_collapses_whitespace(tmp_path: Path):
    text = "# T\n\nA  B\n\n\n\nC"
    doc = Document(path=tmp_path / "a.md", text=text, encoding="utf-8")
    parsed = MarkdownParser().parse(doc)
    norm = Normalizer()
    normalized = norm.apply(parsed)
    joined = "\n".join(s.content for s in normalized.sections)
    assert "A B" in joined
    assert "\n\n\n" not in joined
