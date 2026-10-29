# peer-review-template

**Write better peer reviews faster: a guided questionnaire (summary, contribution, major and minor
issues, type-specific checklist) rendered into a clean report for the authors and a separate
confidential note for the editor.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Reviewing is a core academic duty that is rarely taught. Good reports summarize the paper, separate
major from minor issues, and check the same essentials (methods, statistics, data availability,
limitations) every time. A structured template makes reviews more complete and consistent, and keeps
confidential remarks out of the text sent to authors.

## Features

- Checklists for `empirical`, `computational` and `review` manuscripts
- Fill a JSON answers file (`new`) or answer interactively in the terminal (`interactive`)
- Validation before rendering: recommendation present, summary long enough, major issues backing a
  major-revision/reject recommendation, unanswered checklist items, unprofessional wording
- Markdown report with numbered comments and checklist table; separate editor note with recommendation

## Usage

```bash
pip install .
peer-review-template new -k computational -o review_MS123.json      # edit the JSON
peer-review-template render review_MS123.json -o report.md --editor to_editor.md
peer-review-template interactive -k empirical -o review.json
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
