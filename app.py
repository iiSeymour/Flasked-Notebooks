#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import forms
from glob import glob
from os.path import basename
import IPython.nbformat.current as nbf
from run_ipynb import convert_nb_html, inject_params
from flask import Flask, request, render_template, abort, g

app = Flask(__name__)
app.secret_key = os.urandom(128)


@app.before_request
def before_request():
    g.nbs = [basename(f).split('.')[0] for f in glob('notebooks/*ipynb')]


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/notebook/adder.ipynb", methods=['GET', 'POST'])
def adder():
    """
    Inject input parameters to the adder notebook before rendering
    """
    if request.method == 'POST':
        notebook = nbf.read(open('notebooks/adder.ipynb', 'r'), 'ipynb')
        notebook = inject_params(request.form, notebook)
        html_notebook = convert_nb_html(notebook)
        return render_template('notebook.html', content=html_notebook)
    else:
        params = forms.AdderForm()
        return render_template('adder.html', form=params)


@app.route("/notebook/<notebook>")
def notebook(notebook):
    """
    Dynamically render IPython Notebook
    """
    try:
        notebook = nbf.read(open('notebooks/%s' % notebook, 'r'), 'ipynb')
    except IOError:
        abort(418)
    html_notebook = convert_nb_html(notebook)
    return render_template('notebook.html', content=html_notebook)


if __name__ == "__main__":
    app.run(debug=True)
