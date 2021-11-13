#!/usr/bin/env python
"""Flask Python API example"""

from flask import Flask

app = Flask(__name__)


@app.route('/')
def success_message():
    """Endpoint / for success message"""
    return 'Success!'


@app.route('/ping')
def ok_message():
    """Endpoint /ping for OK message"""
    return 'Ok'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
