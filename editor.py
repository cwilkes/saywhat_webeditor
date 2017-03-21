import requests
import json
import csv
from flask import render_template
from flask_table import Table, Col, LinkCol
from collections import defaultdict
from operator import itemgetter

"""
Creates the page for use in editing
"""
CHOICES_LEVEL_IMPACT = list(range(6))
CHOICES_DESIGN_DISC = ['architect', 'electrical engineer', 'mechanical engineer', 'contractor']


# overrides for Flask-Table columns
# see https://pypi.python.org/pypi/Flask-Table/

class MultiChoiceCol(Col):
    """Makes a dropdown menu with a highlighted option."""
    def __init__(self, name, class_name=None, **kwargs):
        html_class = {'class': class_name if class_name else name}
        super(MultiChoiceCol, self).__init__(name, td_html_attrs=html_class, **kwargs)
        # choices is set after creation
        self.choices = None

    def td_format(self, raw_content):
        ret = list()
        content, GUID = raw_content
        ret.append('<select data-id="{}" data-col="{}">'.format(GUID, self.name))
        for choice in self.choices:
            entry = '<option '
            if choice == content:
                entry += 'selected '
            entry += 'value="{0}">{0}</option>'.format(choice)
            ret.append(entry)
        ret.append('</select>')
        return '\r\n'.join(ret)


class ImageCol(Col):
    """Makes an image tag."""
    def td_format(self, content):
        return '<img src="{0}" width=100 height=100/>'.format(content)

class LinkyCol(Col):
    """Makes a link entry."""
    def td_format(self, content,display=None):
        return '<a href="{0}">{1}</a>'.format(content, content if display is None else content)


# our tables

class FullTable(Table):
    def __init__(self, name, users, design_discipline_affecteds, user_types, level_of_impacts, **kwargs):
        super(FullTable, self).__init__(name, users, **kwargs)
        self.username.choices = users
        self.design_discipline_affected.choices = design_discipline_affecteds
        self.type_of_user.choices = user_types
        self.level_of_impact.choices = level_of_impacts

    GUID=Col('GUID')
    x=Col('x')
    y=Col('y')
    z=Col('z')
    spherical_image = ImageCol('spherical_image')
    audio = LinkyCol('audio')
    audio_transcription = Col('audio_transcription')
    username = MultiChoiceCol('username')
    design_discipline_affected = MultiChoiceCol('design_discipline_affected')
    type_of_user = MultiChoiceCol('type_of_user')
    estimated_cost_of_change = Col('estimated_cost_of_change')
    estimated_time_of_design_change = Col('estimated_time_of_design_change')
    level_of_impact = MultiChoiceCol('level_of_impact')


class FullEntry(object):
    def __init__(self, GUID, x,y,z,spherical_image,audio,audio_transcription,username,design_discipline_affected,type_of_user,estimated_cost_of_change,estimated_time_of_design_change,level_of_impact):
        self.GUID = GUID
        self.x = x
        self.y = y
        self.z = z
        self.spherical_image = spherical_image
        self.audio = audio
        self.audio_transcription = audio_transcription
        self.username = username, GUID
        self.design_discipline_affected = design_discipline_affected, GUID
        self.type_of_user = type_of_user, GUID
        self.estimated_cost_of_change = estimated_cost_of_change
        self.estimated_time_of_design_change = estimated_time_of_design_change
        self.level_of_impact = level_of_impact, GUID


def get_data(url):
    r = requests.get(url)
    csv_reader = csv.DictReader(r.text.split('\r\n'))
    return sorted(list(csv_reader), key=itemgetter('GUID'), reverse=True)


def _mk_user_list(data):
    return sorted(set(map(itemgetter('username'), data)))


def _get_unique_col(data, name):
    return sorted(set(map(itemgetter(name), data)))


def edit_page(url_csv):
    data = get_data(url_csv)
    items = list()
    users = _mk_user_list(data)
    design_discipline_affecteds = _get_unique_col(data, 'design discipline affected')
    user_types = _get_unique_col(data, 'type of user')
    for row in data:
        r2 = dict()
        for k, v in row.items():
            k2 = k.replace(' ', '_')
            r2[k2] = v
        items.append(FullEntry(**r2))
    full_table = FullTable(items, users, design_discipline_affecteds, user_types, [str(_) for _ in range(6)])
    return render_template('index.html', full_table=full_table)
