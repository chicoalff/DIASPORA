from pathlib import Path
import json

from modules.metadata import Record
from modules.export import Exporter


def test_export_jsonl(tmp_path: Path):
    recs = [
        Record(
            id="1",
            source="a.md",
            source_name="a.md",
            section="t",
            language="pt",
            created_at="2025-11-10T00:00:00Z",
            tags="x,y",
            title="A",
            text="conteúdo",
        )
    ]
    out = tmp_path / "out"
    out.mkdir()
    path = Exporter().export(records=recs, output_dir=out, basename="dataset", formats=["jsonl"])
    assert path.exists()
    with path.open(encoding="utf-8") as f:
        line = f.readline()
        obj = json.loads(line)
        assert obj["title"] == "A"
