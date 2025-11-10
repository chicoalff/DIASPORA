from modules.parse_md import Section
from modules.normalize import NormalizedDocument
from modules.chunker import Chunker


def test_chunker_splits_long_text():
    sec = Section(level=1, title="T", content=" ".join(["palavra"] * 1200), meta={})
    ndoc = NormalizedDocument(sections=[sec])
    ch = Chunker(target_tokens=200, hard_max_tokens=300, overlap_tokens=20)
    parts = ch.split(ndoc)
    assert len(parts) > 1
    assert all(len(p.content.split()) <= 300 for p in parts)
