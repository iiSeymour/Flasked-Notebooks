#!/usr/bin/env python
# -*- coding: utf-8 -*0

"""
Given an IPython Notebook JSON object, run all code cells, replace 
output cell with updated output and return the HTLM representation 

Adapted from: https://gist.github.com/minrk/2620735
"""

import re
import os
import sys
import time
import base64
from Queue import Empty
from BeautifulSoup import BeautifulSoup
from IPython.config import Config
from collections import defaultdict
from IPython.nbconvert import HTMLExporter
from IPython.nbformat.current import reads, NotebookNode
try:
    from IPython.kernel import KernelManager
except ImportError:
    from IPython.zmq.blockingkernelmanager import BlockingKernelManager as KernelManager


def run_cell(shell, iopub, cell, timeout=60):

    shell.execute(cell.input)
    # wait for finish
    shell.get_msg(timeout=timeout)
    outs = []

    while True:
        try:
            msg = iopub.get_msg(timeout=0.2)
        except Empty:
            break
        msg_type = msg['msg_type']
        if msg_type in ('status', 'pyin'):
            continue
        elif msg_type == 'clear_output':
            outs = []
            continue

        content = msg['content']

        out = NotebookNode(output_type=msg_type)

        if msg_type == 'stream':
            out.stream = content['name']
            out.text = content['data']
        elif msg_type in ('display_data', 'pyout'):
            out['metadata'] = content['metadata']
            for mime, data in content['data'].iteritems():
                attr = mime.split('/')[-1].lower()
                # this gets most right, but fix svg+html, plain
                attr = attr.replace('+xml', '').replace('plain', 'text')
                setattr(out, attr, data)
            if msg_type == 'pyout':
                out.prompt_number = content['execution_count']
        elif msg_type == 'pyerr':
            out.ename = content['ename']
            out.evalue = content['evalue']
            out.traceback = content['traceback']
        else:
            print "unhandled iopub msg:", msg_type

        outs.append(out)

    return outs


def run_notebook(nb):
    """
    Run each code cell in a given notebook and update with the new output
    """
    km = KernelManager()
    km.start_kernel(extra_arguments=['--pylab=inline'])
    try:
        kc = km.client()
        kc.start_channels()
        iopub = kc.iopub_channel
    except AttributeError:
        # IPython 0.13
        kc = km
        kc.start_channels()
        iopub = kc.sub_channel
    shell = kc.shell_channel

    shell.execute("pass")
    shell.get_msg()
    while True:
        try:
            iopub.get_msg(timeout=1)
        except Empty:
            break

    for ws in nb.worksheets:
        for cell in ws.cells:
            if cell.cell_type != 'code':
                continue
            try:
                cell.outputs = run_cell(shell, iopub, cell)
            except Exception as e:
                return -1

    kc.stop_channels()
    km.shutdown_kernel()
    del km
    return nb


def convert_nb_html(nb):
    """
    Convert a notebooks output to HTML
    """
    nb = run_notebook(nb)
    config = Config({'HTMLExporter': {'default_template': 'basic'}})
    exportHtml = HTMLExporter(config=config)
    html, resources = exportHtml.from_notebook_node(nb)
    soup = BeautifulSoup(html)
    return ''.join(map(str, soup.findAll("div", {"class": ["output", "text_cell_render border-box-sizing rendered_html"]})))
