# docmeta

**docmeta** — небольшая CLI-утилита, которая показывает метаданные PDF- и
DOCX-файлов, выбранных пользователем. Помогает проверить собственные документы
перед публикацией.

**docmeta** is a small CLI utility that displays metadata from user-selected PDF
and DOCX files. Use it to review your own documents before publishing them.

## Возможности / Features

- Работает локально: файлы и метаданные никуда не отправляются.
- Поддерживает PDF и DOCX.
- Показывает автора, название, даты и другие встроенные свойства файла.
- Выводит результат на русском или английском либо в JSON.
- Не сканирует каталоги и не загружает файлы с сайтов.

## Требования / Requirements

- Python 3.10 или новее
- `pypdf` (устанавливается автоматически)

## Установка / Installation

```bash
python -m pip install .
```

Для разработки:

```bash
python -m pip install -e .
```

## Использование / Usage

Проверить один или несколько файлов:

```bash
docmeta report.pdf draft.docx --lang ru
```

Вывести машиночитаемый JSON:

```bash
docmeta report.pdf --json
```

Если команда `docmeta` ещё недоступна в PATH:

```bash
python -m docmeta --lang en report.pdf
```

Пример JSON:

```json
[
  {
    "path": "report.pdf",
    "format": "PDF",
    "metadata": {
      "title": "Quarterly report",
      "author": "Example Author"
    },
    "error": null
  }
]
```

Код завершения `0` означает, что все файлы обработаны; `1` — что при проверке
хотя бы одного файла возникла ошибка.

## Безопасность и ограничения / Safety and limitations

Запускайте проверку только для своих файлов или документов, которые вам
разрешено аудировать. Утилита читает только метаданные явно указанных файлов,
не извлекает текст документа и не выполняет сетевые запросы. Метаданные могут
содержать личную информацию — проверяйте их перед публикацией.

Use the tool only on your own files or documents you are authorized to audit.
It reads metadata from explicitly selected files, does not extract document
text, and makes no network requests. Metadata may contain personal information;
review it before publishing.

## Запуск тестов / Run tests

```bash
python -m unittest discover -s tests -v
```

## План развития / Roadmap

- Расширить тесты на повреждённые файлы и граничные случаи.
- Добавить поддержку других распространённых форматов документов.
- Подготовить короткие демонстрации и инструкции для сообщества.

## Продвижение / Sharing

- **Habr:** опубликовать разбор утечки метаданных и показать локальную проверку
  своих документов.
- **Reddit:** поделиться проектом в подходящем сообществе, например
  r/Python, следуя правилам публикации проектов.
- **Telegram:** написать в тематические чаты Python и информационной
  безопасности, сначала проверив их правила саморекламы.

## Лицензия / License

MIT. См. [LICENSE](LICENSE).
