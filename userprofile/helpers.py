# -*- coding: utf-8 -*-

"""WebHelpers used in userprofile."""

from webhelpers import date, feedgenerator, html, number, misc, text

def bold(text):
    return html.literal('<strong>%s</strong>' % text)