#!/usr/bin/env python3
"""Test sheet reading"""
from sheetreader.Logbook import Entry, MarkdownDecorator


def test_entries_sheet_has_expected_columns(logbook):
    expected_columns = [
        "no",
        "day",
        "start",
        "end",
        "country",
        "timezone",
        "place",
        "placeDetail",
        "time",
        "distance",
        "elevation",
        "descent",
        "altitude",
        "flats",
        "weather",
        "food_cost",
        "other",
        "accommodation",
        "fx",
        "overnight",
        "summary",
        "lostItems",
        "internal_notes",
        "cost_p_day",
        "total_time",
        "km_cumulative",
        "average_speed",
        "break_time",
    ]

    for c in expected_columns:
        assert c in logbook.header


def test_sheet_has_correct_values(logbook):
    for e in logbook.entries:
        assert isinstance(e, Entry)
        if e.is_cycling_day:
            assert e.distance > 0
        else:
            assert e.distance is None


def test_current_entry_markdown(logbook, example_entry_markdown):
    entry = logbook.entry(example_entry_markdown["iso_date"])
    assert (
        MarkdownDecorator(entry, template_file="entry_v2.md").get_markdown()
        == example_entry_markdown["markdown"]
    )


# def test_entry_all_markdown(logbook, mock_yield_markdown):
#     for entry_markdown in mock_yield_markdown:
#         iso_date = entry_markdown["iso_date"]
#         entry = logbook.entry(entry_markdown["iso_date"])
#         template_file = "entry_v2.md"
#         assert (
#             MarkdownDecorator(entry, template_file=template_file).get_markdown()
#             == entry_markdown["markdown"]
#         )
