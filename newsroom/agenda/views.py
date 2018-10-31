from newsroom.agenda import blueprint

import flask

from flask import current_app as app
from eve.methods.get import get_internal
from eve.render import send_response
from superdesk import get_resource_service

from newsroom.template_filters import is_admin_or_internal
from newsroom.topics import get_user_topics
from newsroom.navigations.navigations import get_navigations_by_company
from newsroom.auth import get_user, login_required
from newsroom.utils import get_entity_or_404, is_json_request, get_json_or_400
from newsroom.wire.views import update_action_list
from newsroom.agenda.email import send_coverage_request_email
from newsroom.companies import section
from newsroom.notifications import push_user_notification


@blueprint.route('/agenda')
@login_required
@section('agenda')
def index():
    return flask.render_template('agenda_index.html', data=get_view_data())


@blueprint.route('/bookmarks_agenda')
@login_required
def bookmarks():
    data = get_view_data()
    data['bookmarks'] = True
    return flask.render_template('agenda_index.html', data=data)


@blueprint.route('/agenda/<_id>')
@login_required
def item(_id):
    item = get_entity_or_404(_id, 'agenda')

    user = get_user()
    if not is_admin_or_internal(user):
        item.get('event', {}).pop('files', None)

    if is_json_request(flask.request):
        return flask.jsonify(item)

    if 'print' in flask.request.args:
        template = 'agenda_item_print.html'
        update_action_list([_id], 'prints', force_insert=True)
        return flask.render_template(template, item=item)

    data = get_view_data()
    data['item'] = item
    return flask.render_template('agenda_index.html', data=data, title=item.get('name', item.get('headline')))


@blueprint.route('/agenda/search')
@login_required
def search():
    response = get_internal('agenda')
    return send_response('agenda', response)


def get_view_data():
    user = get_user()
    topics = get_user_topics(user['_id']) if user else []
    return {
        'user': str(user['_id']) if user else None,
        'company': str(user['company']) if user and user.get('company') else None,
        'topics': [t for t in topics if t.get('topic_type') == 'agenda'],
        'formats': [{'format': f['format'], 'name': f['name']} for f in app.download_formatters.values()
                    if 'agenda' in f['types']],
        'navigations': get_navigations_by_company(str(user['company']) if user and user.get('company') else None,
                                                  product_type='agenda'),
        'saved_items': get_resource_service('agenda').get_saved_items_count(),
        'coverage_types': app.config['COVERAGE_TYPES'],
    }


@blueprint.route('/agenda/request_coverage', methods=['POST'])
@login_required
def request_coverage():
    user = get_user(required=True)
    data = get_json_or_400()
    assert data.get('item')
    assert data.get('message')
    item = get_entity_or_404(data.get('item'), 'agenda')
    send_coverage_request_email(user, data.get('message'), item['_id'])
    return flask.jsonify(), 201


@blueprint.route('/agenda_bookmark', methods=['POST', 'DELETE'])
@login_required
def bookmark():
    data = get_json_or_400()
    assert data.get('items')
    update_action_list(data.get('items'), 'bookmarks', item_type='agenda')
    push_user_notification('saved_items', count=get_resource_service('agenda').get_saved_items_count())
    return flask.jsonify(), 200


@blueprint.route('/agenda_watch', methods=['POST', 'DELETE'])
@login_required
def follow():
    data = get_json_or_400()
    assert data.get('items')
    update_action_list(data.get('items'), 'watches', item_type='agenda')
    push_user_notification('saved_items', count=get_resource_service('agenda').get_saved_items_count())
    return flask.jsonify(), 200
