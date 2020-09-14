import logging
import os
import sys

import requests
import yaml
from jinja2 import Environment, FileSystemLoader


def show_args(function):
    def proceed(*args):
        fn = "[fn] {}".format(function.__name__)
        if args:
            fn += "; [args] {}".format(list(args))
        logging.debug(fn)
        return function(*args)

    return proceed


def load_project(map_file):
    """Read and parse YAML project map"""
    with open(map_file, 'r') as project_file:
        try:
            return yaml.safe_load(project_file)
        except yaml.YAMLError as ex:
            logging.critical(ex)
            sys.exit(1)


@show_args
def get_categories():
    """Retrieve existing categories."""
    r = requests.get(API_URL + '/categories.json', headers=headers)
    logging.debug("[{}]: {}".format(r.status_code, r.json()))

    try:
        category_list = r.json()['category_list']['categories']
        _categories = []
        for _category in category_list:
            _categories.append({'id': _category['id'], 'name': _category['name'], 'slug': _category['slug'],
                                'color': _category['color']})
        return _categories

    except KeyError:
        logging.warning("response doesn't contain target keys")
        return None


@show_args
def get_topic_from_category(_id):
    """Retrieve all topics from a target category."""
    r = requests.get(API_URL + "/c/{}.json".format(_id), headers=headers)
    logging.debug("[{}]: {}".format(r.status_code, r.json()))

    try:
        topic_list = r.json()['topic_list']['topics']
        _topics = []
        for _topic in topic_list:
            _topics.append(
                {'id': _topic['id'], 'title': _topic['title'], 'slug': _topic['slug'], 'closed': _topic['closed']})
        return _topics

    except KeyError:
        logging.warning("response doesn't contain target keys")
        return None


@show_args
def delete_topic(_id):
    """Delete a topic with a target ID."""
    r = requests.delete(API_URL + "/t/{}.json".format(_id), headers=headers)
    logging.debug("[{}] {}".format(r.status_code, r.text))


@show_args
def create_category(_name, _color, text_color="000000"):
    """Create category with given parameters."""
    data = {"name": _name, "color": _color, "text_color": text_color}
    r = requests.post(API_URL + "/categories.json", headers=headers, data=data)
    logging.debug("[{}]: {}".format(r.status_code, r.json()))

    try:
        _category_id = r.json()['category']['id']
        return _category_id

    except KeyError:
        logging.warning("response doesn't contain target keys")
        return None


@show_args
def create_topic(title, raw, _category_id):
    """Create topic within given category with given parameters."""
    data = {"title": title, "raw": raw, "category": _category_id}
    r = requests.post(API_URL + "/posts.json", headers=headers, data=data)
    logging.debug("[{}]: {}".format(r.status_code, r.json()))


@show_args
def bootstrap_project():
    """Create categories and topics on managed Discourse server from project map"""
    colors = ["F7941D", "BF1E2E", "3AB54A", "25AAE2"]
    project = load_project("project.yml")
    for _category in project:
        _category_id = create_category(_category, colors.pop())
        logging.info("created category: {}; id: {}".format(_category, _category_id))
        for _topic in project[_category]:
            create_topic(_topic, _topic, _category_id)


@show_args
def render_html(_categories):
    """Render contents with given categories and topics bundle"""
    bundle = {}
    for category in _categories:
        name = category['name']
        color = category['color']
        category_url = "{}/c/{}".format(API_URL, category['slug'])
        if name not in ['Staff', 'Uncategorized']:
            bundle[name] = {"color": color, "category_url": category_url, "topics": []}
            for topic in get_topic_from_category(category['id']):
                title = topic['title']
                closed = topic['closed']
                topic_url = "{}/t/{}".format(API_URL, topic['slug'])
                if not title.startswith('About '):
                    bundle[name]["topics"].append({"title": title, "topic_url": topic_url, "closed": closed })

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('map.html.j2')

    for b in bundle:
        print("{}: {}".format(b, bundle[b]))

    output = template.render(bundle=bundle)
    print(output)


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stdout,
        level=logging.INFO)

    API_URL = os.environ.get('API_URL')
    API_KEY = os.environ.get('API_KEY')
    API_USER = os.environ.get('API_USER')
    if not API_URL or not API_KEY or not API_USER:
        logging.warning("please export API_{URL,KEY,USER} [!]")
        exit(1)

    headers = {
        "Api-Key": API_KEY,
        "Api-Username": API_USER
    }

    categories = get_categories()
    logging.info("categories: %s" % categories)

    render_html(categories)
