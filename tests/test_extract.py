from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from pypdf import PdfWriter

from docmeta.extract import MetadataError, extract_metadata


class ExtractMetadataTests(unittest.TestCase):
    def test_extracts_pdf_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=72, height=72)
            writer.add_metadata({"/Title": "Portfolio sample", "/Author": "Test Author"})
            with path.open("wb") as file:
                writer.write(file)

            file_format, metadata = extract_metadata(path)

        self.assertEqual(file_format, "PDF")
        self.assertEqual(metadata["title"], "Portfolio sample")
        self.assertEqual(metadata["author"], "Test Author")

    def test_extracts_docx_core_properties(self) -> None:
        core_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <cp:coreProperties
          xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
          xmlns:dc="http://purl.org/dc/elements/1.1/">
          <dc:title>Portfolio sample</dc:title>
          <dc:creator>Test Author</dc:creator>
          <cp:lastModifiedBy>Editor</cp:lastModifiedBy>
        </cp:coreProperties>"""

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.docx"
            with ZipFile(path, "w") as archive:
                archive.writestr("docProps/core.xml", core_xml)

            file_format, metadata = extract_metadata(path)

        self.assertEqual(file_format, "DOCX")
        self.assertEqual(metadata["title"], "Portfolio sample")
        self.assertEqual(metadata["author"], "Test Author")
        self.assertEqual(metadata["last_modified_by"], "Editor")

    def test_rejects_unsupported_file_type(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            path.write_text("not a supported document", encoding="utf-8")

            with self.assertRaises(MetadataError):
                extract_metadata(path)


if __name__ == "__main__":
    unittest.main()
