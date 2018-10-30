import os
import arrow
import flask
import hashlib

from flask import current_app as app
from eve.utils import str_to_date
from flask_babel import format_time, format_date, format_datetime
from superdesk.text_utils import get_text, get_word_count
from superdesk.utc import utcnow


def parse_date(datetime):
    """Return datetime instance for datetime."""
    if isinstance(datetime, str):
        try:
            return str_to_date(datetime)
        except ValueError:
            return arrow.get(datetime).datetime
    return datetime


def datetime_short(datetime):
    if datetime:
        return format_datetime(parse_date(datetime), 'short')


def datetime_long(datetime):
    if datetime:
        return format_datetime(parse_date(datetime), "dd/MM/yyyy HH:mm")


def date_header(datetime):
    return format_datetime(parse_date(datetime if datetime else utcnow()), 'EEEE, MMMM d, yyyy')


def time_short(datetime):
    if datetime:
        return format_time(parse_date(datetime), 'hh:mm')


def date_short(datetime):
    if datetime:
        return format_date(parse_date(datetime), 'short')


def plain_text(html):
    return get_text(html, lf_on_block=True) if html else ''


def word_count(html):
    return get_word_count(html or '')


def is_admin(user=None):
    if user:
        return user.get('user_type') == 'administrator'
    return flask.session.get('user_type') == 'administrator'


def is_admin_or_internal(user=None):
    if user:
        return user.get('user_type') == 'administrator' or user.get('user_type') == 'internal'
    return flask.session.get('user_type') == 'administrator' or \
        flask.session.get('user_type') == 'internal'


def newsroom_config():
    port = int(os.environ.get('PORT', '5000'))
    return {
        'websocket': os.environ.get('NEWSROOM_WEBSOCKET_URL', 'ws://localhost:%d' % (port + 100, )),
        'time_format': flask.current_app.config['CLIENT_TIME_FORMAT'],
        'date_format': flask.current_app.config['CLIENT_DATE_FORMAT'],
        'coverage_date_format': flask.current_app.config['CLIENT_COVERAGE_DATE_FORMAT'],
        'display_abstract': flask.current_app.config['DISPLAY_ABSTRACT'],
    }


def hash_string(value):
    """Return SHA256 hash for given string value."""
    return hashlib.sha256(str(value).encode('utf-8')).hexdigest()


def get_date():
    return utcnow()


def sidenavs(blueprint=None):
    def blueprint_matches(nav, blueprint):
        return not nav.get('blueprint') or not blueprint or nav['blueprint'] == blueprint

    return [nav for nav in app.sidenavs if blueprint_matches(nav, blueprint)]
