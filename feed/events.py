#!/usr/bin/env python
""" calendar.py
    =========
    Author: Anthony Sutardja
    Last modified: 2015-03-15
    =========
    Methods to fetch calendar information about a company.
"""
import httplib
import time
from collections import namedtuple

from pyquery import PyQuery as pq

BASE_URL = "www.google.com"


class CalendarItem(object):
    """ Abstraction for keeping track of a calendar item."""

    def __init__(self, title, date):
        self.title = str(title)
        self.date = time.strptime(date, '%b %d, %Y %I:%M%p')


def create_calendar_query_path(symbol):
    """Return the query path for the calendar query."""
    return '/finance/events?q={symbol}&output=html'.format(symbol=symbol)


def get_calendar_rows_from_google(symbol):
    """Return a list of tuples that scrapes the calendar info off Google."""
    # Fetch data
    conn = httplib.HTTPConnection(BASE_URL)
    conn.request('GET', create_calendar_query_path(symbol))

    # Get response
    response = conn.getresponse().read()

    # Load as DOM
    dom = pq(response)

    rows = []
    for tr in dom('tr'):
        rows.append(tuple([td.text for td in tr.findall('td')]))

    return rows


def filter_rows_by_earnings(rows):
    """Return a list of tuples that contain earnings relevant info."""
    return [row for row in rows if row[0] and 'earnings' in row[0].lower()]


def convert_rows_to_datetime_tuple(rows):
    """Return a list of calendar items."""
    return [CalendarItem(row[0], row[1]) for row in rows]