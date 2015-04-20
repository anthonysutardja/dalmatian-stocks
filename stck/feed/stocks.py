#!/usr/bin/env python
""" stocks.py
    =========
    Author: Anthony Sutardja
    Last modified: 2015-03-15
    =========
    Methods to fetch stock quotes from external sources.
"""
import httplib
import os
import string
import sys
import time

os.environ['TZ'] = 'US/Eastern'
time.tzset()  # need to reset for eastern timezone


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
    query_path = "/finance/getprices?i=86400&p=3d&f=d,c&df=cpct&q="

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


def get_time_series_from_yahoo(symbol, period):

    base_url = "chartapi.finance.yahoo.com"
    query_path = "/instrument/1.0/{symbol}/chartdata;type=quote;range={period}/csv/"

    if period not in ('1d', '5d', '30d', '1m', '3m', '6m', '1y'):
        period = '1d'

    symbol = validate_stock_symbol(symbol)

    # Make request
    conn = httplib.HTTPConnection(base_url)
    conn.request("GET", query_path.format(symbol=symbol, period=period))
    response = conn.getresponse().read().rsplit()
    response = [r.split(',') for r in response if ':' not in r]
    response = [r for r in response if len(r) == 6]

    results = []
    for r in response:
        if period[-1] == 'd':
            # use epoch time
            t = time.localtime(float(r[0]))
        else:
            # use strptime
            t = time.strptime(r[0], '%Y%m%d')
        t = time.strftime('%Y-%m-%dT%H:%M:%SZ', t)
        price = float(r[1])
        results.append({'time': t, 'quote': price})
    return results


def get_time_series_from_google(symbol, period):
    # NOTE DATA IS INCONSISTENT UPON MULTIPLE QUERIES..
    base_url = "www.google.com"
    QUERY_PATHS = {
        '1d': '/finance/getprices?i=234&p=1d&f=d,c&df=cpct&q=',
        '5d': '/finance/getprices?i=1170&p=5d&f=d,c&df=cpct&q=',
        '1m': '/finance/getprices?i=7020&p=30d&f=d,c&df=cpct&q=',
        '3m': '/finance/getprices?i=21060&p=90d&f=d,c&df=cpct&q=',
        '1y': '/finance/getprices?i=60840&p=260d&f=d,c&df=cpct&q=',
        'default': '/finance/getprices?i=234&p=1d&f=d,c&df=cpct&q=',
    }

    if period not in QUERY_PATHS:
        period = 'default'

    # Query must contain symbols in capital letters
    symbol = validate_stock_symbol(symbol)

    # Make request
    conn = httplib.HTTPConnection(base_url)
    conn.request("GET", QUERY_PATHS[str(period)] + symbol)
    response = conn.getresponse().read().rsplit()

    # Check if symbol was valid.
    # strips away 'EXCHANGE%3D' from first line of response
    checkQuote = str(response[0][11:])
    if (checkQuote == 'UNKNOWN+EXCHANGE'):
        raise ValueError("Symbol is not listed.")

    # Return last quote
    results = response[7:]
    results = [tuple(r.split(',')) for r in results if 'TIMEZONE_OFFSET' not in r]

    formatted_results = []
    for date, price in results:
        t = time.localtime(float(date[1:]))
        t = time.strftime('%Y-%m-%dT%H:%M:%SZ', t)

        res = {'time': t, 'quote': float(price)}
        formatted_results.append(res)
    return formatted_results


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
