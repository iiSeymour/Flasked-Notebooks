#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from glob import glob
from os.path import basename
from run_ipynb import convert_nb_html
import IPython.nbformat.current as nbf
from flask import Flask, render_template, abort, g

app = Flask(__name__)


@app.before_request
def before_request():
    g.nbs = [basename(f).split('.')[0] for f in glob('notebooks/*ipynb')]


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/notebook/<notebook>")
def notebook(notebook):
    try:
        notebook = nbf.read(open('notebooks/%s' % notebook, 'r'), 'ipynb')
    except IOError:
        abort(418)
    html_notebook= convert_nb_html(notebook)
    return render_template('notebook.html', content=html_notebook)


if __name__ == "__main__":
    app.run(debug=True)
