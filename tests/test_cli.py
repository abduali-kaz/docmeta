from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from docmeta.cli import main


class CliTests(unittest.TestCase):
    def test_russian_help_is_localized(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit):
            main(["--lang", "ru", "--help"])

        self.assertIn("Проверка метаданных", output.getvalue())
        self.assertIn("Язык вывода", output.getvalue())

    def test_json_reports_missing_files_and_returns_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing_path = str(Path(directory) / "missing.pdf")
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = main(["--json", missing_path])

        report = json.loads(output.getvalue())[0]
        self.assertEqual(exit_code, 1)
        self.assertEqual(report["path"], missing_path)
        self.assertEqual(report["metadata"], {})
        self.assertIsNotNone(report["error"])

    def test_language_option_can_follow_the_file_path(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as result:
            main(["--help", "--lang=ru"])

        self.assertEqual(result.exception.code, 0)
        self.assertIn("Проверка метаданных", output.getvalue())


if __name__ == "__main__":
    unittest.main()
