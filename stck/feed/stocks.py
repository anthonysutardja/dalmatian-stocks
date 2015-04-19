#!/usr/bin/env python
""" stocks.py
    =========
    Author: Anthony Sutardja
    Last modified: 2015-03-15
    =========
    Methods to fetch stock quotes from external sources.
"""
import httplib
import string
import sys


def validate_stock_symbol(symbol):
    """Return the symbol if it is valid."""
    symbol = str(symbol).upper()
    charlist = string.ascii_uppercase + "." + "-"
    for ch in symbol:
        if ch not in charlist:
            raise ValueError("Must contain letters A-Z and/or .")
    return symbol


def get_quote_from_google(symbol):
    """Return a tuple containing market quote information for a symbol.

    Information is requested from Google.
    """
    base_url = "www.google.com"
    query_path = "/finance/getprices?i=60&p=1d&f=d,o,h,l,c,v&df=cpct&q="

    # Query must contain symbols in capital letters
    symbol = validate_stock_symbol(symbol)

    # Make request
    conn = httplib.HTTPConnection(base_url)
    conn.request("GET", query_path + symbol)
    response = conn.getresponse().read().rsplit()

    # Check if symbol was valid.
    # strips away 'EXCHANGE%3D' from first line of response
    checkQuote = str(response[0][11:])
    if (checkQuote == 'UNKNOWN+EXCHANGE'):
        raise ValueError("Symbol is not listed.")

    # Return last quote
    lastReading = response[-1].split(",")
    current, high, low = float(lastReading[1]), float(lastReading[2]), float(lastReading[3])
    return current, high, low


def get_change_from_google(symbol):
    """Return da change."""

    base_url = "www.google.com"
    query_path = "/finance/getprices?i=86400&p=2d&f=d,c&df=cpct&q="

    # Query must contain symbols in capital letters
    symbol = validate_stock_symbol(symbol)

    # Make request
    conn = httplib.HTTPConnection(base_url)
    conn.request("GET", query_path + symbol)
    response = conn.getresponse().read().rsplit()

    # Check if symbol was valid.
    # strips away 'EXCHANGE%3D' from first line of response
    checkQuote = str(response[0][11:])
    if (checkQuote == 'UNKNOWN+EXCHANGE'):
        raise ValueError("Symbol is not listed.")

    # Return last quote
    twoDaysBefore = response[-2].split(",")
    old = float(twoDaysBefore[1])

    oneDayBefore = response[-1].split(",")
    current = float(oneDayBefore[1])
    return (current - old) / old * 100.0


def get_formatted_change(symbol):
    change = get_change_from_google(symbol)

    if change > 0.0:
        sign = '+'
    else:
        sign = ''
    return '{sign}{change:.2f}%'.format(sign=sign, change=change)


def get_quote_from_yahoo(symbol):
    """Return a tuple containing market quote information for a symbol.

    Information is requested from Yahoo.
    """

    symbol = validate_stock_symbol(symbol)
    base_url = "chartapi.finance.yahoo.com"
    query_path = "/instrument/1.0/" + symbol + "/chartdata;type=quote;range=1d/csv/"
    conn = httplib.HTTPConnection(base_url)

    # Make request
    conn.request("GET", query_path)
    response = conn.getresponse().read().rsplit()

    # Return last quote
    lastReading = response[-1].split(",")
    current, high, low = float(lastReading[1]), float(lastReading[2]), float(lastReading[3])
    return current, high, low


if __name__ == "__main__":
    symbol = sys.argv[1]
    latest = get_quote_from_yahoo(symbol)
    print """
    {symbol}
    --------
    Current: {curr}
    High:    {high}
    Low:     {low}
    """.format(
        symbol=symbol.upper(),
        curr=latest[0],
        high=latest[1],
        low=latest[1],
    )
