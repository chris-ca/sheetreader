#!/usr/bin/env python3
"""Read Logbook from Google Spreadsheet.

"""

from abc import ABC, abstractmethod
from datetime import datetime
from diskcache import Cache
import logging
import gspread
import jinja2
import config

cache = Cache(config.cache["path"])

logger = logging.getLogger(__name__)


class NoEntryException(Exception):
    pass


class Logbook(ABC):
    """Abstract class for Logbook"""

    @staticmethod
    def load(type_: str, **kwargs):
        """Return Logbook object

        Args:
            type_ (str): "Google"
            **kwargs (dict): Keyword arguments
                used to instantiate child class
        Returns:
            Logbook
        """
        class_ = type_ + "Logbook"
        class_ = globals()[class_]
        obj = class_(**kwargs)
        return obj

    @property
    @abstractmethod
    def entries(self):
        pass


class GoogleLogbook(Logbook):
    """Read Logbook from Google Sheets"""

    auth_file = "service.json"

    def __init__(self, **kwargs):
        """Instantiate class.
        Args:
            **kwargs : Dictionary with Configuration
                ``{
                    "key"       : "GOOGLE-SHEETS-ID_STRING",
                    "auth_file" : "service.json"
                }``
        """
        self.key = kwargs.get("key", None)
        self.file = kwargs.get("file", None)
        self.auth_file = kwargs.get("auth_file", None)

        rows = self.fetch_sheet("entries")

        self._entries = {}
        for i, row in enumerate(rows):
            if i == 0:
                self.set_header(row)
            else:
                try:
                    entry = Entry(row, self.header)
                    if entry.is_valid_entry:
                        self._entries[entry.iso_date] = entry

                except (KeyError, ValueError) as exc:
                    logger.warning("Skipped invalid entry %d", i)
                    raise Exception from exc
        logger.debug(
            "Total entries checked: %d", len(rows)
        )  # pylint: disable=undefined-loop-variable

    def set_header(self, row):
        """Return cleaned header fields"""
        self.header = [f.replace(" ", "_") for f in row]

    def load_sheet(self):
        logger.info(
            "Loading Google Sheet %s using credentials from %s",
            self.key,
            self.auth_file,
        )
        gc = gspread.service_account(filename=self.auth_file)
        return gc.open_by_key(self.key)

    @cache.memoize(expire=config.cache["cache_time_gsheets"])
    def fetch_sheet(self, key):
        """Return all rows fields for the given worksheet"""
        sheet = self.load_sheet()
        ws = sheet.worksheet(key)
        return ws.get_all_values()

    @property
    def entries(self):
        for day in self._entries:  # pylint: disable=consider-using-dict-items
            yield self._entries[day]

    def entry(self, iso_date):
        """Return entry for date.

        Args:
            iso_date str: Date of entry to return, e.g. 2018-06-18
        Returns:
            Entry:
        """
        try:
            return self._entries[iso_date]
        except KeyError as exc:
            msg = ("No logbook entry for %s", iso_date)
            logger.warning(msg)
            raise NoEntryException(msg) from exc


class Entry:
    """Logbook Entry."""

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
        """Assign instance variables as they come at at runtime.

        The following fields are used::

            no, day, start, end, country, timezone, place, placeDetail,
            time, distance, elevation, descent, altitude, flats, weather,
            food_cost, other, accommodation, fx, overnight, summary, lostItems,
            internal_notes, cost_p_day, total_time, km_cumulative,
            average_speed, break_time
        """
        for i, k in enumerate(keys):
            setattr(self, k.replace(" ", "_"), entry[i])

        self.iso_date = self.day  # pylint: disable=access-member-before-definition

        self.year = int(self.iso_date.split("-")[0])
        self.month = int(self.iso_date.split("-")[1])
        self.day = int(self.iso_date.split("-")[2])

        self.datetime = datetime(self.year, self.month, self.day)

        self.set_none_if_empty()
        self.convert_costs_to_float()

    def set_none_if_empty(self):
        # Distance is usually set to '0' for rest days
        # Other fields can also be empty
        for k in ["distance", "elevation", "descent", "altitude", "average_speed"]:
            try:
                # remove , that comes from gogole sheet
                v = getattr(self, k)
                v = float(v.replace(",", ""))
                if v == 0:
                    raise ValueError
            except ValueError:
                v = None

            setattr(self, k, v)

    def convert_costs_to_float(self):
        for k in ["food_cost", "accommodation", "other", "cost_p_day"]:
            try:
                setattr(self, k, float(getattr(self, k).removesuffix(" €")))
            except ValueError:
                setattr(self, k, 0)

    @property
    def is_valid_entry(self):
        return self.is_past_day

    @property
    def is_past_day(self):
        if self.datetime <= datetime.today():
            return True
        return False

    @property
    def is_cycling_day(self):
        return self.distance is not None

    @property
    def is_rest_day(self):
        return self.distance is None

class EntryDecorator(ABC):
    @property
    @abstractmethod
    def content(self):
        pass

class MarkdownEntry(EntryDecorator):
    """Turn Logbook Entry into Markdown."""

    def __init__(self, entry: Entry, template_file="entry_v2.md"):
        template_loader = jinja2.FileSystemLoader(searchpath="./templates")
        template_env = jinja2.Environment(loader=template_loader)
        self.template = template_env.get_template(template_file)
        self.entry = entry

    def __repr__(self):
        return self.__name__+self.day

    @property
    def content(self):
        return self.template.render(e=self.entry)
    # @property
    # def text(self):
    #     return self.get().lstrip() + "\n"

