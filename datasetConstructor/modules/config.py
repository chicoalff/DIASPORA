from typing import List
import logging
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, validator


class IngestionSettings(BaseModel):
    preferred_encodings: List[str] = Field(default_factory=lambda: ["utf-8", "latin-1", "cp1252"])


class NormalizeSettings(BaseModel):
    remove_headers_footers: bool = True
    deduplicate: bool = True
    collapse_whitespace: bool = True
    strip_metadata: bool = True


class ChunkingSettings(BaseModel):
    target_tokens: int = 400
    hard_max_tokens: int = 800
    overlap_tokens: int = 40
    split_on_headings: bool = True

    @validator("hard_max_tokens")
    def validate_limits(cls, v: int, values):
        if "target_tokens" in values and v < values["target_tokens"]:
            raise ValueError("hard_max_tokens deve ser >= target_tokens")
        return v

    @validator("overlap_tokens")
    def validate_overlap(cls, v: int, values):
        if "target_tokens" in values and v >= values["target_tokens"]:
            raise ValueError("overlap_tokens deve ser menor que target_tokens")
        return v


class ExportSettings(BaseModel):
    formats: List[str] = Field(default_factory=lambda: ["jsonl"])


class MetadataSettings(BaseModel):
    default_tags: List[str] = Field(default_factory=list)


class Settings(BaseModel):
    ingestion: IngestionSettings = IngestionSettings()
    normalize: NormalizeSettings = NormalizeSettings()
    chunking: ChunkingSettings = ChunkingSettings()
    export: ExportSettings = ExportSettings()
    metadata: MetadataSettings = MetadataSettings()


def load_settings(path: Path) -> Settings:
    logger = logging.getLogger("settings")
    if not path.exists():
        logger.warning("Arquivo de configuração não encontrado. Usando defaults.")
        return Settings()
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return Settings(**raw)
