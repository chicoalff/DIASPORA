from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
import logging

import chardet


@dataclass
class Document:
    path: Path
    text: str
    encoding: str


class Ingestor:
    def __init__(self, preferred_encodings: Optional[list[str]] = None) -> None:
        self.logger = logging.getLogger("ingestor")
        self.preferred_encodings = preferred_encodings or ["utf-8", "latin-1", "cp1252"]

    def read(self, path: Path) -> Document:
        if not path.exists():
            raise FileNotFoundError(str(path))

        for enc in self.preferred_encodings:
            try:
                text = path.read_text(encoding=enc)
                return Document(path=path, text=text, encoding=enc)
            except UnicodeDecodeError:
                continue

        detected, confidence = self._detect_encoding(path)
        try:
            text = path.read_text(encoding=detected)
            return Document(path=path, text=text, encoding=detected)
        except UnicodeDecodeError as exc:
            self.logger.error("Falha ao decodificar %s (detectado=%s conf=%.2f)", path, detected, confidence)
            raise exc

    def _detect_encoding(self, path: Path) -> Tuple[str, float]:
        data = path.read_bytes()
        guess = chardet.detect(data)
        encoding = guess.get("encoding") or "utf-8"
        confidence = float(guess.get("confidence") or 0.0)
        return encoding, confidence
