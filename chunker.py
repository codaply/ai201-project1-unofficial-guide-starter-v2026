"""Stage 2 of the pipeline: split documents into searchable chunks.

The custom strategy centers one chunk on each sentence within a heading-defined
section. When the 436-character budget permits, it also includes the immediate
previous and next sentences from that same section. Each chunk repeats the
document title and its section heading. Paragraph breaks help detect sentence
boundaries but do not prevent neighboring sentences in one section from sharing
a chunk. A sentence longer than the available budget is split between words as
a last resort. The original fixed-window splitter remains for comparison.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


MAX_PIECE_CHARS = 436
_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.*)$", re.MULTILINE)
_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str
    index: int
    produced_by: str

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """The starter's original fixed-size character splitter with overlap."""
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


@dataclass
class _Section:
    """One heading, or the unheaded opening text, and its paragraphs."""

    heading: str | None
    paragraphs: list[str]


def _extract_title(text: str) -> tuple[str, str]:
    """Take a leading '# ...' title off the text to repeat in each chunk."""
    stripped = text.lstrip()
    if not stripped.startswith("# "):
        return "", text
    first_line, _, rest = stripped.partition("\n")
    return first_line[2:].strip(), rest


def _split_paragraphs(body: str) -> list[str]:
    """Keep paragraph breaks available when detecting sentences."""
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def _split_into_sections(text: str) -> list[_Section]:
    """Keep every section separate; no chunk spans two headings."""
    matches = list(_HEADING_RE.finditer(text))
    sections: list[_Section] = []

    opening_end = matches[0].start() if matches else len(text)
    opening = text[:opening_end].strip()
    if opening:
        sections.append(_Section(heading=None, paragraphs=_split_paragraphs(opening)))

    for i, match in enumerate(matches):
        heading = match.group(0).strip()
        body_start = match.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        sections.append(_Section(heading=heading, paragraphs=_split_paragraphs(body)))

    return sections


def _split_words(text: str, budget: int) -> list[str]:
    """Split an oversized sentence between complete words as a last resort."""
    words = text.split()
    pieces: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}" if current else word
        if len(candidate) <= budget:
            current = candidate
        else:
            if current:
                pieces.append(current)
            # A single word longer than the budget cannot fit without damage.
            # Preserve it intact rather than silently cutting it in half.
            current = word
    if current:
        pieces.append(current)
    return pieces


def _split_sentences(paragraph: str, budget: int) -> list[str]:
    """Return one sentence per fragment, preserving word boundaries."""
    sentences = [s.strip() for s in _SENTENCE_BOUNDARY_RE.split(paragraph) if s.strip()]
    fragments: list[str] = []
    for sentence in sentences:
        if len(sentence) <= budget:
            fragments.append(sentence)
        else:
            fragments.extend(_split_words(sentence, budget))
    return fragments


def _render(title: str, heading: str | None, sentence: str) -> str:
    """Add the source title and section heading to sentence text."""
    parts: list[str] = []
    if title:
        parts.append(f"# {title}")
    if heading:
        parts.append(heading)
    parts.append(sentence)
    return "\n\n".join(parts)


def _fragments_for_section(section: _Section, title: str, budget: int) -> list[str]:
    """Split every paragraph into sentence fragments, including short ones."""
    # Calculate available space with the exact prefix _render() will add.
    prefix = _render(title, section.heading, "")
    room = budget - len(prefix)
    if room < 1:
        raise ValueError("Document title and section heading leave no room for text")

    fragments: list[str] = []
    for paragraph in section.paragraphs:
        fragments.extend(_split_sentences(paragraph, room))
    return fragments


def _context_windows(fragments: list[str], title: str, heading: str | None) -> list[str]:
    """Center each piece on one sentence, with immediate neighbors if they fit.

    The list belongs to one section, so context never crosses a heading. Edge
    sentences have just one neighbor. For an oversized window, keep the focus
    sentence and add each adjacent sentence only while the whole rendered
    piece remains within MAX_PIECE_CHARS.
    """
    windows: list[str] = []
    for i, focus in enumerate(fragments):
        start = i
        end = i + 1
        if i > 0:
            candidate = " ".join(fragments[i - 1:end])
            if len(_render(title, heading, candidate)) <= MAX_PIECE_CHARS:
                start = i - 1
        if i + 1 < len(fragments):
            candidate = " ".join(fragments[start:i + 2])
            if len(_render(title, heading, candidate)) <= MAX_PIECE_CHARS:
                end = i + 2
        windows.append(" ".join(fragments[start:end]))
    return windows


def split_documents(documents: list[Document]) -> list[Chunk]:
    """Create one focus-sentence chunk at a time within each section.

    Each chunk carries its title and heading and includes its immediate prior
    and following sentences when they fit. Those neighboring sentences are
    intentionally repeated between adjacent chunks. A sentence that cannot
    fit the 436-character limit is split at word boundaries as a last resort.
    """
    chunks: list[Chunk] = []
    for doc in documents:
        title, body = _extract_title(doc.text)
        sections = _split_into_sections(body)
        index = 0
        for section in sections:
            fragments = _fragments_for_section(section, title, MAX_PIECE_CHARS)
            for fragment in _context_windows(fragments, title, section.heading):
                chunks.append(
                    Chunk(
                        text=_render(title, section.heading, fragment),
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1
    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
