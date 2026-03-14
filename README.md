# Kanjinetworks-Yomitan

Repo to convert the [kanjinetworks db](https://github.com/acoomans/kanjinetworks) to a yomitan kanji dictionary for use in DaKanji

## Installation

Make sure uv is installed on your system and run

``` bash
uv sync
```

## Usage

Run this command to parse the PDF database and convert it to a yomitan kanji dictionary.

``` bash
uv run kanjinetworks_to_yomitan.py
```

This will also create a `introduction.pdf` with the explanatory notes for the kanjinetworks DB.
