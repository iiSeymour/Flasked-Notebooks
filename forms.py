#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import IntegerField


class AdderForm(Form):
    a = IntegerField('a')
    b = IntegerField('b')
