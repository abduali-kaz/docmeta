from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TypedDict

from .extract import expected_read_errors, extract_metadata


_TEXT = {
    "en": {
        "description": "Inspect metadata in explicitly selected local PDF and DOCX files.",
        "file": "File",
        "format": "Format",
        "no_metadata": "No metadata found.",
        "error": "Error",
        "metadata": "Metadata",
        "usage_hint": "Inspect metadata in your own or authorized documents.",
        "paths_help": "Local PDF/DOCX file paths",
        "lang_help": "Output language",
        "json_help": "Print machine-readable JSON",
    },
    "ru": {
        "description": "Проверка метаданных выбранных локальных файлов PDF и DOCX.",
        "file": "Файл",
        "format": "Формат",
        "no_metadata": "Метаданные не найдены.",
        "error": "Ошибка",
        "metadata": "Метаданные",
        "usage_hint": "Проверяйте свои документы или документы, на аудит которых у вас есть разрешение.",
        "paths_help": "Пути к локальным файлам PDF/DOCX",
        "lang_help": "Язык вывода",
        "json_help": "Вывести данные в формате JSON",
    },
}
_FIELD_LABELS = {
    "en": {
        "title": "Title",
        "author": "Author",
        "subject": "Subject",
        "creator": "Creator",
        "producer": "Producer",
        "created": "Created",
        "modified": "Modified",
        "keywords": "Keywords",
        "last_modified_by": "Last modified by",
        "category": "Category",
        "revision": "Revision",
    },
    "ru": {
        "title": "Название",
        "author": "Автор",
        "subject": "Тема",
        "creator": "Программа-создатель",
        "producer": "Производитель PDF",
        "created": "Создан",
        "modified": "Изменён",
        "keywords": "Ключевые слова",
        "last_modified_by": "Последний редактор",
        "category": "Категория",
        "revision": "Редакция",
    },
}


class Report(TypedDict):
    path: str
    format: str | None
    metadata: dict[str, str]
    error: str | None


def _parser(language: str) -> argparse.ArgumentParser:
    text = _TEXT[language]
    parser = argparse.ArgumentParser(
        prog="docmeta",
        description=text["description"],
    )
    parser.add_argument("paths", nargs="+", type=Path, help=text["paths_help"])
    parser.add_argument("--lang", choices=("ru", "en"), default="en", help=text["lang_help"])
    parser.add_argument("--json", action="store_true", help=text["json_help"])
    return parser


def _requested_language(argv: list[str]) -> str:
    bootstrap_parser = argparse.ArgumentParser(add_help=False)
    bootstrap_parser.add_argument("--lang", default="en")
    parsed, _ = bootstrap_parser.parse_known_args(argv)
    return parsed.lang if parsed.lang in _TEXT else "en"


def _printable(value: object) -> str:
    return "".join(character for character in str(value) if character.isprintable())


def _inspect(path: Path) -> Report:
    try:
        file_format, metadata = extract_metadata(path)
    except expected_read_errors() as error:
        return {
            "path": str(path),
            "format": None,
            "metadata": {},
            "error": _printable(error),
        }
    return {"path": str(path), "format": file_format, "metadata": metadata, "error": None}


def _print_text(reports: list[Report], language: str) -> None:
    text = _TEXT[language]
    labels = _FIELD_LABELS[language]

    for index, report in enumerate(reports):
        if index:
            print()
        print(f"{text['file']}: {_printable(report['path'])}")
        if report["error"] is not None:
            print(f"{text['error']}: {report['error']}")
            continue

        print(f"{text['format']}: {report['format']}")
        if not report["metadata"]:
            print(text["no_metadata"])
            continue

        print(f"{text['metadata']}:")
        for key, value in report["metadata"].items():
            print(f"  {labels.get(key, key)}: {value}")


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    args = _parser(_requested_language(arguments)).parse_args(arguments)
    reports = [_inspect(path) for path in args.paths]

    if args.json:
        json.dump(reports, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        print(_TEXT[args.lang]["usage_hint"])
        _print_text(reports, args.lang)

    return 1 if any(report["error"] is not None for report in reports) else 0
