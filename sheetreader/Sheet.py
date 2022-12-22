#!/usr/bin/env python3
import os, sys
import gspread
from datetime import datetime
from diskcache import Cache
import config

cache = Cache(config.cache["path"])


class NoEntryException(Exception):
    pass


class Logbook:
    auth_file = "service.json"
    _entries = {}
    heading = []

    def __init__(self, **kwargs):
        self.key = kwargs.get("key", None)
        self.file = kwargs.get("file", None)
        self.auth_file = kwargs.get("auth_file", None)

        entries = self.fetch_entries()

        for i, entry in enumerate(entries):
            if i == 0:
                self.heading = [e.replace(" ", "_") for e in entry]
            else:
                try:
                    entry = LogbookEntry(entry, self.heading)
                    if entry.is_valid_entry:
                        self._entries[entry.iso_date] = entry

                except:
                    print("Skipped invalid: " + entry)

    @cache.memoize(expire=config.cache["duration"])
    def fetch_entries(self):
        gc = gspread.service_account(filename=self.auth_file)
        sheet = gc.open_by_key(self.key)
        ws = sheet.worksheet("entries")
        return ws.get_all_values()

    @property
    def entries(self):
        for day in self._entries.keys():
            yield self._entries[day]

    def entry(self, iso_date):
        try:
            return self._entries[iso_date]
        except KeyError:
            raise NoEntryException("No logbook entry for " + iso_date)


class LogbookEntry:
    time = 0

    def __repr__(self):
        return (
            "Logbook:"
            + " "
            + self.iso_date
            + " "
            + self.country
            + " "
            + self.place
            + " "
            + self.summary
        )

    def __init__(self, entry, keys):
        """assign all keys as they come from the spreadsheet"""
        for i, k in enumerate(keys):
            setattr(self, k.replace(" ", "_"), entry[i])

        self.iso_date = self.day

        self.year = int(self.iso_date.split("-")[0])
        self.month = int(self.iso_date.split("-")[1])
        self.day = int(self.iso_date.split("-")[2])

        self.datetime = datetime(self.year, self.month, self.day)
        try:
            self.distance = float(self.distance)
        except ValueError:
            self.distance = None
        try:
            self.average_speed = float(self.average_speed)
        except ValueError:
            self.average_speed = None

    @property
    def is_valid_entry(self):
        return self.is_past_day

    @property
    def is_past_day(self):
        if self.datetime <= datetime.today():
            return True
        else:
            return False

    @property
    def is_cycling_day(self):
        return self.distance > 0

    @property
    def is_rest_day(self):
        return self.distance == 0


class MarkdownDecorator:
    markdown = ""

    def __init__(self, l: LogbookEntry):
        self.entry = l

    def __repr__(self):
        return self.get_markdown()

    def add_headline(self, n, s):
        self.markdown += "\n" + n * "#" + " " + s

    def add_general_stats(self):
        entry = self.entry
        self.markdown += f"\n- **Tag**: #{entry.no}"

    def add_distance(self):
        entry = self.entry

        if entry.time and entry.distance:
            self.markdown += f"\n- **Unterwegs**: von {entry.start}-{entry.end} Uhr, Fahrzeit: {entry.time} h"
            self.markdown += (
                f"\n  - {entry.distance} km (⌀ {entry.average_speed:.{0}f} kph)"
            )
            if entry.elevation:
                self.markdown += f" ({entry.elevation} m up, {entry.descent} m down)"
            self.markdown += f"\n  - **Gesamt**: {entry.km_cumulative} km"
        else:
            # self.markdown +=  "\n- Kein Fahrtag"
            pass

    def add_place(self):
        entry = self.entry
        self.markdown += f"\n- **Ort**: {entry.place} ({entry.country})"

    def add_costs(self):
        entry = self.entry

        try:
            food_cost = int(entry.food_cost.removesuffix(" €"))
        except ValueError:
            food_cost = 0

        try:
            accommodation = int(entry.accommodation.removesuffix(" €"))
        except ValueError:
            accommodation = 0

        try:
            other = int(entry.other.removesuffix(" €"))
        except ValueError:
            other = 0

        self.markdown += f"\n- **Ausgaben**: {entry.cost_p_day}"
        if food_cost > 0:
            self.markdown += f" (Essen {food_cost})"
        if accommodation > 0:
            self.markdown += f" (Schlafen {accommodation})"
        if other > 0:
            self.markdown += f" (Sonst. {other})"

    def add_place_details(self):
        entry = self.entry
        self.markdown += f"\n- **Unterkunft**: {entry.overnight}"
        if entry.placeDetail != "":
            self.markdown += f" ({entry.placeDetail})"
        if entry.altitude != "":
            self.markdown += f" ({entry.altitude} hm)"

    @property
    def text(self):
        return self.get_markdown().lstrip() + "\n"

    def get_markdown(self):
        entry = self.entry
        self.add_headline(2, "Logbook")
        self.add_general_stats()
        self.add_distance()
        self.add_place()
        self.add_place_details()
        self.add_costs()
        if entry.summary:
            self.markdown += "\n### Summary\n" + entry.summary
        if entry.internal_notes:
            self.markdown += "\n### Notes\n" + entry.internal_notes

        return self.markdown
