from __future__ import annotations

from pathlib import Path
from typing import Final
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class MetadataError(ValueError):
    """Raised when a supported file cannot provide readable metadata."""


_PDF_FIELDS: Final[dict[str, str]] = {
    "/title": "title",
    "/author": "author",
    "/subject": "subject",
    "/creator": "creator",
    "/producer": "producer",
    "/creationdate": "created",
    "/moddate": "modified",
    "/keywords": "keywords",
}
_DOCX_FIELDS: Final[dict[str, str]] = {
    "title": "title",
    "subject": "subject",
    "creator": "author",
    "keywords": "keywords",
    "lastModifiedBy": "last_modified_by",
    "created": "created",
    "modified": "modified",
    "category": "category",
    "revision": "revision",
}
_MAX_CORE_XML_SIZE: Final = 1_000_000
_MAX_VALUE_LENGTH: Final = 1_000


def _clean(value: object) -> str:
    text = " ".join(str(value).split())
    text = "".join(character for character in text if character.isprintable())
    if len(text) > _MAX_VALUE_LENGTH:
        return text[: _MAX_VALUE_LENGTH - 3] + "..."
    return text


def _add_value(values: dict[str, str], key: str, value: object) -> None:
    text = _clean(value)
    if text:
        values[key] = text


def _extract_pdf(path: Path) -> dict[str, str]:
    reader = PdfReader(str(path), strict=False)
    values: dict[str, str] = {}
    if reader.metadata is None:
        return values

    for source_key, value in reader.metadata.items():
        target_key = _PDF_FIELDS.get(str(source_key).lower())
        if target_key is not None and value is not None:
            _add_value(values, target_key, value)
    return values


def _extract_docx(path: Path) -> dict[str, str]:
    with ZipFile(path) as archive:
        try:
            core_properties = archive.getinfo("docProps/core.xml")
        except KeyError:
            raise MetadataError("DOCX core properties were not found") from None

        if core_properties.file_size > _MAX_CORE_XML_SIZE:
            raise MetadataError("DOCX core properties XML is unexpectedly large")

        root = ElementTree.fromstring(archive.read(core_properties))

    values: dict[str, str] = {}
    for element in root:
        local_name = element.tag.rsplit("}", 1)[-1]
        target_key = _DOCX_FIELDS.get(local_name)
        if target_key is not None and element.text:
            _add_value(values, target_key, element.text)
    return values


def extract_metadata(path: Path) -> tuple[str, dict[str, str]]:
    """Read metadata from one explicitly selected PDF or DOCX file."""
    if not path.is_file():
        raise FileNotFoundError(f"File does not exist: {path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "PDF", _extract_pdf(path)
    if suffix == ".docx":
        return "DOCX", _extract_docx(path)
    raise MetadataError("Unsupported file type; supported formats are PDF and DOCX")


def expected_read_errors() -> tuple[type[Exception], ...]:
    """Return file-format errors the CLI can report without a traceback."""
    return (OSError, PdfReadError, BadZipFile, ElementTree.ParseError, MetadataError)
