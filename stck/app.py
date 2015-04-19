#!/usr/bin/env python
import time

from flask import Flask
from flask import jsonify, render_template

from feed.events import get_last_and_next_earnings_dates
from feed.stocks import get_quote_from_google
from feed.stocks import get_formatted_change
from feed.stocks import get_time_series_from_yahoo


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


def get_general_info(symbol):
    earnings = get_last_and_next_earnings_dates(symbol)
    change = get_formatted_change(symbol)
    lastEarnings = None if earnings['earlier'] is None else time.strftime('%Y-%m-%dT%H:%M:%SZ', earnings['earlier'].date)
    nextEarnings = None if earnings['later'] is None else time.strftime('%Y-%m-%dT%H:%M:%SZ', earnings['later'].date)

    quote, _1, _2 = get_quote_from_google(symbol)

    return dict(
        symbol=symbol.upper(),
        name=None,
        price=quote,
        change=change,
        nextEarnings=nextEarnings,
        lastEarnings=lastEarnings,
    )


@app.route('/api/stocks/<symbols>/general-info')
def get_general_stock_info_group(symbols):
    symbolsList = symbols.split(',')
    ret = []
    for symbol in symbolsList:
        ret.append(get_general_info(symbol))
    return jsonify(results=ret)


@app.route('/api/stock/<symbol>/general-info')
def get_general_stock_info_individual(symbol, period):
    data = get_time_series_from_yahoo(symbol, period)

    # Supports only 1d, 5d, 90 day or 3 months, or 1 year.
    return jsonify(**data)


@app.route('/api/stock/<symbol>/data/period/<period>')
def get_symbol_data(symbol, period):
    data = get_time_series_from_yahoo(symbol, period)
    return jsonify(
        symbol=symbol,
        period=period,
        data=data,
    )


if __name__ == '__main__':
    app.run(debug=True)
