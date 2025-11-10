from dataclasses import dataclass
from typing import List
import logging
import re

from .parse_md import ParsedDocument, Section


@dataclass
class NormalizedDocument:
    sections: List[Section]


class Normalizer:
    def __init__(
        self,
        remove_headers_footers: bool = True,
        deduplicate: bool = True,
        collapse_whitespace: bool = True,
        strip_metadata: bool = True,
    ) -> None:
        self.logger = logging.getLogger("normalizer")
        self.remove_headers_footers = remove_headers_footers
        self.deduplicate = deduplicate
        self.collapse_whitespace = collapse_whitespace
        self.strip_metadata = strip_metadata

    def apply(self, parsed: ParsedDocument) -> NormalizedDocument:
        sections: List[Section] = []
        seen_hashes: set[str] = set()

        header_footer_cand = self._estimate_header_footer_candidates(parsed.text) if self.remove_headers_footers else set()

        for sec in parsed.sections:
            content = sec.content
            if self.remove_headers_footers and header_footer_cand:
                content = self._remove_candidates(content, header_footer_cand)
            if self.strip_metadata:
                content = self._strip_yaml_frontmatter(content)
            if self.collapse_whitespace:
                content = self._collapse_ws(content)
            if self.deduplicate:
                h = self._stable_hash(f"{sec.level}|{sec.title}|{content}")
                if h in seen_hashes:
                    continue
                seen_hashes.add(h)
            sections.append(Section(level=sec.level, title=sec.title, content=content, meta=sec.meta))
        return NormalizedDocument(sections=sections)

    def _estimate_header_footer_candidates(self, text: str) -> set[str]:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        counts: dict[str, int] = {}
        for ln in lines:
            counts[ln] = counts.get(ln, 0) + 1
        threshold = max(3, int(len(lines) * 0.02))
        return {ln for ln, c in counts.items() if c >= threshold and len(ln) <= 80}

    def _remove_candidates(self, content: str, candidates: set[str]) -> str:
        out_lines: List[str] = []
        for ln in content.splitlines():
            s = ln.strip()
            if s in candidates:
                continue
            out_lines.append(ln)
        return "\n".join(out_lines).strip()

    def _strip_yaml_frontmatter(self, content: str) -> str:
        if content.startswith("---"):
            return re.sub(r"^---[\s\S]*?---\s*", "", content, count=1, flags=re.MULTILINE)
        return content

    def _collapse_ws(self, content: str) -> str:
        content = re.sub(r"[ \t]+", " ", content)
        content = re.sub(r"\n{3,}", "\n\n", content)
        return content.strip()

    def _stable_hash(self, s: str) -> str:
        import hashlib
        return hashlib.sha1(s.encode("utf-8")).hexdigest()
