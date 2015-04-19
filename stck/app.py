#!/usr/bin/env python
import time

from flask import Flask
from flask import jsonify, render_template

from feed.events import get_last_and_next_earnings_dates
from feed.stocks import get_quote_from_google
from feed.stocks import get_formatted_change


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
def get_general_stock_info_individual(symbol):
    data = get_general_info(symbol)

    return jsonify(**data)


if __name__ == '__main__':
    app.run(debug=True)
