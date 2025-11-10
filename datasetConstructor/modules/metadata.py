from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import logging
import uuid

import langid
from slugify import slugify

from .chunker import Chunk


@dataclass
class Record:
    id: str
    source: str
    source_name: str
    section: str
    language: str
    created_at: str
    tags: str
    title: str
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MetadataEnricher:
    def __init__(self, default_tags: list[str] | None = None) -> None:
        self.logger = logging.getLogger("metadata")
        self.default_tags = default_tags or []

    def enrich(self, chunk: Chunk, source_path: Path) -> Record:
        lang, _ = langid.classify(chunk.content) if chunk.content else ("unknown", 0.0)
        source_name = source_path.name
        section_slug = slugify(chunk.title or "documento")
        record_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_path.as_posix()}::{chunk.id}::{chunk.section_index}"))

        return Record(
            id=record_id,
            source=str(source_path.resolve()),
            source_name=source_name,
            section=section_slug,
            language=lang,
            created_at=datetime.utcnow().isoformat(timespec="seconds") + "Z",
            tags=",".join(self.default_tags),
            title=chunk.title or "Documento",
            text=chunk.content,
        )
