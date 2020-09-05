import logging
import os
import sys

import requests
import yaml


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
            _topics.append({'id': _topic['id'], 'title': _topic['title'], 'slug': _topic['slug']})
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
def create_category(name, color, text_color="000000"):
    """Create category with given parameters."""
    data = {"name": name, "color": color, "text_color": text_color}
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
        for topic in project[_category]:
            create_topic(topic, topic, _category_id)


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

    for category in categories:
        name = category['name']
        color = category['color']
        category_url = "{}/c/{}".format(API_URL, category['slug'])
        if name not in ['Staff', 'Uncategorized']:
            print("<h1>{} ({}) [{}]</h1>".format(name, category_url, color))
            print("<ul>")
            for topic in get_topic_from_category(category['id']):
                title = topic['title']
                topic_url = "{}/t/{}".format(API_URL, topic['slug'])
                if not title.startswith('About '):
                    print("  <li>{} ({})</li>".format(title, topic_url))
            print("</ul>")
        # logging.info("{}/{}:".format(category['name'], category['id']))
        # logging.info("  {}".format(get_topic_from_category(category['id'])))
