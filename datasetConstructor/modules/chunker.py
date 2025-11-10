from dataclasses import dataclass
from typing import List
import logging
import math

from .normalize import NormalizedDocument
from .parse_md import Section


@dataclass
class Chunk:
    id: str
    title: str
    level: int
    content: str
    section_index: int


class Chunker:
    def __init__(
        self,
        target_tokens: int = 400,
        hard_max_tokens: int = 800,
        overlap_tokens: int = 40,
        split_on_headings: bool = True,
    ) -> None:
        self.logger = logging.getLogger("chunker")
        self.target = target_tokens
        self.hard_max = hard_max_tokens
        self.overlap = overlap_tokens
        self.split_on_headings = split_on_headings

    def split(self, doc: NormalizedDocument) -> List[Chunk]:
        chunks: List[Chunk] = []
        seq = 0
        for idx, sec in enumerate(doc.sections):
            if not sec.content:
                continue
            if self._approx_tokens(sec.content) <= self.hard_max:
                seq += 1
                chunks.append(self._mk_chunk(sec, idx, seq))
                continue

            parts = self._smart_split(sec.content)
            for part in parts:
                tmp_sec = Section(level=sec.level, title=sec.title, content=part, meta=sec.meta)
                seq += 1
                chunks.append(self._mk_chunk(tmp_sec, idx, seq))
        return chunks

    def _smart_split(self, text: str) -> List[str]:
        sentences = self._split_sentences(text)
        out: List[str] = []
        buf: List[str] = []
        buf_tokens = 0
        for s in sentences:
            stoks = self._approx_tokens(s)
            if buf_tokens + stoks > self.hard_max:
                out.append(self._join(buf))
                buf = self._apply_overlap(buf)
                buf_tokens = self._approx_tokens(self._join(buf))
            buf.append(s)
            buf_tokens += stoks
            if buf_tokens >= self.target:
                out.append(self._join(buf))
                buf = self._apply_overlap(buf)
                buf_tokens = self._approx_tokens(self._join(buf)) if buf else 0
        if buf:
            out.append(self._join(buf))
        return [x.strip() for x in out if x.strip()]

    def _apply_overlap(self, buf: List[str]) -> List[str]:
        if not buf or self.overlap <= 0:
            return []
        total = self._approx_tokens(self._join(buf))
        if total <= self.overlap:
            return buf
        out: List[str] = []
        acc = 0
        for s in reversed(buf):
            t = self._approx_tokens(s)
            out.insert(0, s)
            acc += t
            if acc >= self.overlap:
                break
        return out

    def _join(self, parts: List[str]) -> str:
        return " ".join(p.strip() for p in parts)

    def _split_sentences(self, text: str) -> List[str]:
        import re
        return re.split(r"(?<=[\.\!\?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÄËÏÖÜ])", text.strip())

    def _approx_tokens(self, text: str) -> int:
        words = text.strip().split()
        return max(1, int(math.ceil(len(words) * 1.0)))
    
    def _mk_chunk(self, sec: Section, idx: int, seq: int) -> Chunk:
        return Chunk(
            id=f"{idx}-{seq}",
            title=sec.title,
            level=sec.level,
            content=sec.content.strip(),
            section_index=idx,
        )
