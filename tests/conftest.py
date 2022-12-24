#!/usr/bin/env python3
"""Global config/fixtures for pytest"""

import pytest
from sheetreader.logbook import Logbook
import glob
import re
import config

LOGBOOK_PATTERN = re.compile(
    r"(.*)(^## Logbook.*?)(\n^### Location.+|\n^## [^#]*.+|\Z)",
    flags=re.MULTILINE + re.DOTALL,
)


@pytest.fixture()
def logbook():
    return Logbook.load(type_="Google", **config.logbook)


@pytest.fixture()
def example_entry_markdown():
    with open("tests/fixtures/entry_1366.md", encoding="UTF-8") as fh:
        return {"iso_date": "2022-03-14", "day": 1366, "markdown": fh.read()}


@pytest.fixture()
def mock_yield_markdown():
    result = []
    for filename in glob.glob("/home/cw/Coding/diarytools/tempdiary/2022/**/*.md"):
        try:
            m = re.search(r"([0-9]{4})/([0-9]{2})/([0-9]{2}).md", filename)
            iso_date = m.group(1) + "-" + m.group(2) + "-" + m.group(3)

            with open(filename, encoding="UTF-8") as fh:
                contents = fh.read()
                m = re.search(LOGBOOK_PATTERN, contents)
                if m is None:
                    continue

                markdown = m.group(2)

                result.append(
                    {
                        "iso_date": iso_date,
                        "markdown": markdown,
                    }
                )
        except AttributeError:
            # FIXME
            pass

    return result
