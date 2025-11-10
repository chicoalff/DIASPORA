from dataclasses import dataclass, field
from typing import List, Dict, Any
import logging
import re

from markdown_it import MarkdownIt
from markdown_it.token import Token


@dataclass
class Section:
    level: int
    title: str
    content: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedDocument:
    text: str
    sections: List[Section]
    links: List[str]
    code_blocks: List[str]
    tables: List[str]
    blockquotes: List[str]
    lists: List[str]


class MarkdownParser:
    def __init__(self) -> None:
        self.logger = logging.getLogger("parser")
        self.md = MarkdownIt("commonmark").enable("table").enable("strikethrough")

    def parse(self, doc) -> ParsedDocument:
        tokens = self.md.parse(doc.text)
        sections = self._extract_sections(tokens, doc.text)
        links = self._extract_links(doc.text)
        code_blocks = self._extract_fences(tokens, doc.text)
        tables = self._extract_tables(tokens, doc.text)
        blockquotes = self._extract_blockquotes(tokens, doc.text)
        lists = self._extract_lists(tokens, doc.text)
        return ParsedDocument(
            text=doc.text,
            sections=sections,
            links=links,
            code_blocks=code_blocks,
            tables=tables,
            blockquotes=blockquotes,
            lists=lists,
        )

    def _extract_sections(self, tokens: List[Token], full_text: str) -> List[Section]:
        sections: List[Section] = []
        stack: List[Section] = []
        current_text_parts: List[str] = []

        def flush_current(level: int, title: str) -> None:
            if stack:
                stack[-1].content = "".join(current_text_parts).strip()
                sections.append(stack.pop())
                current_text_parts.clear()
            stack.append(Section(level=level, title=title.strip(), content=""))

        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t.type == "heading_open":
                level = int(t.tag[1])
                inline = tokens[i + 1]
                title = inline.content if inline.type == "inline" else ""
                flush_current(level, title)
                i += 2
                continue
            if t.type in ("paragraph_open", "bullet_list_open", "ordered_list_open", "blockquote_open", "fence", "table_open"):
                content = self._render_block(tokens, i)
                current_text_parts.append(content + "\n")
            i += 1

        if stack:
            stack[-1].content = "".join(current_text_parts).strip()
            sections.append(stack.pop())

        if not sections:
            sections = [Section(level=1, title="Documento", content=full_text)]
        return sections

    def _render_block(self, tokens: List[Token], idx: int) -> str:
        open_token = tokens[idx]
        if open_token.type == "fence":
            return open_token.content
        level = 1
        i = idx + 1
        parts: List[str] = []
        while i < len(tokens) and not (tokens[i].type == open_token.type.replace("_open", "_close") and level == 1):
            tok = tokens[i]
            if tok.type.endswith("_open"):
                level += 1
            elif tok.type.endswith("_close"):
                level -= 1
            elif tok.type == "inline":
                parts.append(tok.content)
            i += 1
        return "\n".join(parts).strip()

    def _extract_fences(self, tokens: List[Token], _: str) -> List[str]:
        return [t.content for t in tokens if t.type == "fence"]

    def _extract_tables(self, tokens: List[Token], _: str) -> List[str]:
        tables: List[str] = []
        buf: List[str] = []
        depth = 0
        for t in tokens:
            if t.type == "table_open":
                depth = 1
                buf = []
                continue
            if depth > 0:
                if t.type == "inline":
                    buf.append(t.content)
                if t.type == "table_close":
                    tables.append("\n".join(buf).strip())
                    depth = 0
        return tables

    def _extract_blockquotes(self, tokens: List[Token], _: str) -> List[str]:
        quotes: List[str] = []
        buf: List[str] = []
        depth = 0
        for t in tokens:
            if t.type == "blockquote_open":
                depth += 1
                continue
            if depth > 0:
                if t.type == "inline":
                    buf.append(t.content)
                if t.type == "blockquote_close":
                    quotes.append("\n".join(buf).strip())
                    buf = []
                    depth -= 1
        return quotes

    def _extract_lists(self, tokens: List[Token], _: str) -> List[str]:
        lists: List[str] = []
        buf: List[str] = []
        depth = 0
        for t in tokens:
            if t.type in ("bullet_list_open", "ordered_list_open"):
                depth += 1
                continue
            if depth > 0:
                if t.type == "inline":
                    buf.append(t.content)
                if t.type in ("bullet_list_close", "ordered_list_close"):
                    lists.append("\n".join(buf).strip())
                    buf = []
                    depth -= 1
        return lists

    def _extract_links(self, text: str) -> List[str]:
        pattern = re.compile(r"\[(?:[^\]]+)\]\((https?://[^\s)]+)\)")
        return pattern.findall(text)
