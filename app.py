# -*- coding: utf-8 -*-

import json
import editor

from flask import Flask, request, make_response, render_template, jsonify, logging
import requests
import os
from urllib.parse import parse_qs

URL_CSV = os.environ['SAY_WHAT_CSV_URL']
URL_UPDATE = os.environ['SAY_WHAT_UPDATE_URL']

app = Flask(__name__)

def _parse_form_data():
    """Returns a generator of tuples of form ids to their single values."""
    form_data = str(request.get_data())
    if form_data[:2] == "b'":
        # looks like   b'A=1&B=2'
        form_data = form_data[2:-1]
    for key, values in parse_qs(form_data).items():
        yield (key, values[0])


@app.route('/update', methods=['POST',])
def update():
    data = dict(_parse_form_data())
    r = requests.post(URL_UPDATE, data=json.dumps(data))
    return jsonify(dict(r=r.text))

@app.route('/')
def index():
    return editor.edit_page(URL_CSV)


if __name__ == '__main__':
    app.run(debug=True)
