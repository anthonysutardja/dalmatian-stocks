#!/usr/bin/env python
""" stocks.py
    =========
    Author: Anthony Sutardja
    Last modified: 2012-07-02
    =========
    Lost in translation.
"""
import httplib
import string
import sys


def validate_stock_symbol(symbol):
    """Docstring hur"""
    symbol = str(symbol).upper()
    charlist = string.ascii_uppercase + "." + "-"
    for ch in symbol:
        if ch not in charlist:
            raise ValueError("Must contain letters A-Z and/or .")
    return symbol


def get_quote_from_google(symbol, retry=0):
    """Gets the quote of a symbol"""
    NUM_RETRY = 5
    base_url = "www.google.com"
    query_path = "/finance/getprices?i=60&p=1d&f=d,o,h,l,c,v&df=cpct&q="

    # Query must contain symbols in capital letters
    try:
        symbol = validate_stock_symbol(symbol)
    except ValueError:
        raise ValueError("Symbol is not valid")

    # Make request
    conn = httplib.HTTPConnection(base_url)
    conn.request("GET", query_path + symbol)
    response = conn.getresponse().read().rsplit()

    if len(response) == 0:
        raise ValueError("Server did not respond")

    # Check if symbol was valid.
    # strips away 'EXCHANGE%3D' from first line of response
    checkQuote = str(response[0][11:])
    if (checkQuote == 'UNKNOWN+EXCHANGE'):
        raise ValueError("Symbol is not listed.")

    # Return last quote
    lastReading = response[-1].split(",")
    current, high, low = float(lastReading[1]), float(lastReading[2]), float(lastReading[3])
    return current, high, low


def get_quote_from_yahoo(symbol):
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
