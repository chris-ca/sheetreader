#!/usr/bin/env python3
import pytest

from sheetreader.Logbook import Logbook, Entry, MarkdownDecorator

config = __import__("config-test")

@pytest.fixture()
def logbook():
    return Logbook.load(type_="Google", **config.logbook)

def test_read_sheet(logbook):
    for e in logbook.entries:
        assert type(e) == Entry

def test_sheet_has_columns(logbook):
    expected_columns = ['no','day','start','end','country','timezone','place','placeDetail','time','distance','elevation','descent','altitude','flats','weather','food_cost','other','accommodation','fx','overnight','summary','lostItems','internal_notes','cost_p_day','total_time','km_cumulative','average_speed','break_time']

    for c in expected_columns:
        assert c in logbook.heading

def test_sheet_has_correct_values(logbook):
    for e in logbook.entries:
        assert type(e.distance) == float or e.distance == None
        assert type(e.average_speed) == float or e.average_speed == None

def test_markdown(logbook):
    for e in logbook.entries:
        assert '**Tag**' in MarkdownDecorator(e).get_markdown()
        assert '**Ort**' in MarkdownDecorator(e).get_markdown()
        assert '**Unterkunft**' in MarkdownDecorator(e).get_markdown()

