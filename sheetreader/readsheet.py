#!/usr/bin/env python3
""" read logbook entries and display as markdown """
import logging
from sheetreader.Logbook import Logbook, MarkdownDecorator

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s - %(module)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
logging.basicConfig(level=logging.INFO)

config = __import__("config-test")

logbook = Logbook.load('Google', **config.logbook)

for i, e in enumerate(logbook.entries):
    print(i, MarkdownDecorator(e))
