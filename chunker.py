"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below replaces the plain, fixed-size chunker with a
heading-scoped, paragraph-aware strategy: headings mark subject boundaries,
so a chunk never spans two headings. Within one heading's content,
paragraphs are packed together while they fit a size budget; a paragraph
too long to fit alone is divided at sentence endings, never mid-sentence
or mid-word.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch
back to it, write down what you saw, and move on. That's a real observation
about your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


# Milestone 3's size cap. Chosen from the corpus, not from config.CHUNK_SIZE:
# observed sections run 123-691 characters and observed paragraphs run
# 71-451, so 800 lets most sections stand as one piece with room to spare.
# config.CHUNK_SIZE is left alone — it still drives the fallback's fixed
# windows.
MAX_PIECE_CHARS = 800

_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.*)$", re.MULTILINE)
_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
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


# ---------------------------------------------------------------------------
# Milestone 3: heading-scoped, paragraph-aware chunker
# ---------------------------------------------------------------------------
#
# This maps directly onto the strategy as written, one rule at a time:
#
#   "I will use headings to understand what each section is about" ->
#       a heading marks where one subject ends and the next begins. A chunk
#       never spans two headings. Text before the first heading (10 of 14
#       docs have some) is its own headingless section, same rule.
#
#   "group neighboring paragraphs when they discuss the same subject and
#    fit within my 800-character size limit" ->
#       paragraphs under the SAME heading are, by construction, the same
#       subject, so they're packed together into one piece as long as it
#       stays under budget.
#
#   "I will start a new piece when ... adding more text would make it too
#    large" ->
#       once the next paragraph would push the running piece over
#       MAX_PIECE_CHARS, that piece is closed and a new one starts — still
#       under the same heading if the section itself doesn't fit in one
#       piece.
#
#   "I will keep the document title with its content" ->
#       a leading "# ..." title is pulled off the top of the document and
#       carried into every piece, so a piece read on its own still says
#       what document it's from.
#
#   "I will keep paragraphs intact whenever possible. If a paragraph is too
#    long to fit by itself, I will divide it at sentence endings. I will
#    avoid cutting a sentence or word in the middle." ->
#       a paragraph is only ever split when it can't fit the budget alone
#       (title + heading overhead counted). It's split at sentence
#       boundaries; a single sentence too long even by itself falls back to
#       word boundaries as the last resort, never a mid-word cut.
#
# NOT implemented: "I may include text from the next section if it adds
# useful context and still fits." That line is explicitly discretionary
# ("may"), and deciding which specific neighboring sections are related
# enough to share a piece is a judgment call about content, not something
# this function can determine on its own — hard-coding a rule for it would
# just be reintroducing my own logic in place of yours again. If you want
# that behavior, tell me the concrete rule (e.g. "merge a trailing section
# under N characters into the piece before it", or a specific heading name
# like "Practical notes") and it can be added exactly as specified.


@dataclass
class _Section:
    """One heading (or the un-headed opening text) and the paragraphs under it."""

    heading: str | None
    paragraphs: list[str]


def _extract_title(text: str) -> tuple[str, str]:
    """
    Pull a leading "# ..." title off the very start of the document, if
    there is one, so it can be carried into every piece for identification.
    Returns (title, remaining_text). If the document doesn't open with a
    top-level heading, title is "" and the whole text is returned unchanged.
    """
    stripped = text.lstrip()
    if not stripped.startswith("# "):
        return "", text
    first_line, _, rest = stripped.partition("\n")
    return first_line[2:].strip(), rest


def _split_paragraphs(body: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def _split_into_sections(text: str) -> list[_Section]:
    """Break document text (title already removed) into heading-delimited sections."""
    matches = list(_HEADING_RE.finditer(text))
    sections: list[_Section] = []

    opening_end = matches[0].start() if matches else len(text)
    opening = text[:opening_end].strip()
    if opening:
        sections.append(_Section(heading=None, paragraphs=_split_paragraphs(opening)))

    for i, m in enumerate(matches):
        heading = m.group(0).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        sections.append(_Section(heading=heading, paragraphs=_split_paragraphs(body)))

    return sections


def _split_sentences(paragraph: str, budget: int) -> list[str]:
    """
    Pack a paragraph's sentences into fragments no longer than `budget`,
    never cutting a sentence in half — except as a last resort (below) when
    a single sentence alone is longer than the whole budget.
    """
    sentences = [s for s in _SENTENCE_BOUNDARY_RE.split(paragraph) if s]
    packed: list[str] = []
    current = ""

    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence
        if not current or len(candidate) <= budget:
            current = candidate
        else:
            packed.append(current)
            current = sentence
    if current:
        packed.append(current)

    # A single sentence that's still too long can't be split without cutting
    # mid-sentence, which the brief rules out first. Fall back to word
    # boundaries only for that sentence, so at least no word gets cut.
    fragments: list[str] = []
    for piece in packed:
        if len(piece) <= budget:
            fragments.append(piece)
        else:
            fragments.extend(_split_words(piece, budget))
    return fragments


def _split_words(text: str, budget: int) -> list[str]:
    words = text.split(" ")
    pieces: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip() if current else word
        if not current or len(candidate) <= budget:
            current = candidate
        else:
            pieces.append(current)
            current = word
    if current:
        pieces.append(current)
    return pieces


def _render(title: str, heading: str | None, paragraphs: list[str]) -> str:
    """Render one piece's text: title, then heading (if any), then paragraphs."""
    parts: list[str] = []
    if title:
        parts.append(f"# {title}")
    if heading:
        parts.append(heading)
    if paragraphs:
        parts.append("\n\n".join(paragraphs))
    return "\n\n".join(parts)


def _fragments_for_section(section: _Section, title: str, budget: int) -> list[str]:
    """Turn one section's paragraphs into fragments, splitting only the ones
    that can't fit the budget on their own once title/heading overhead
    (which every piece containing them will have to carry) is counted."""
    overhead = len(title) + len(section.heading or "") + 4  # blank-line joins
    room = max(budget - overhead, 1)

    fragments: list[str] = []
    for paragraph in section.paragraphs:
        if len(paragraph) <= room:
            fragments.append(paragraph)
        else:
            fragments.extend(_split_sentences(paragraph, room))
    return fragments


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks: headings mark subject boundaries (a chunk
    never spans two headings); paragraphs under the same heading are packed
    together while they fit MAX_PIECE_CHARS (title and heading included); a
    paragraph too long to fit alone is divided at sentence endings, never
    mid-sentence or mid-word; the document's title travels with every piece.

    `produced_by` is set to "chunker.py::split_documents" — `app.py chunks`
    prints it, and it belongs in the README's Sample Chunks section.
    """
    budget = MAX_PIECE_CHARS
    chunks: list[Chunk] = []

    for doc in documents:
        title, body = _extract_title(doc.text)
        sections = _split_into_sections(body)

        index = 0
        for section in sections:
            fragments = _fragments_for_section(section, title, budget)

            buffer: list[str] = []
            for fragment in fragments:
                candidate = buffer + [fragment]
                if not buffer or len(_render(title, section.heading, candidate)) <= budget:
                    buffer = candidate
                    continue
                chunks.append(
                    Chunk(
                        text=_render(title, section.heading, buffer),
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1
                buffer = [fragment]
            if buffer:
                chunks.append(
                    Chunk(
                        text=_render(title, section.heading, buffer),
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
