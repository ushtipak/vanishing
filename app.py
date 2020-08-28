import logging
import os
import sys

import requests


def show_args(function):
    def proceed(*args):
        fn = "[fn] {}".format(function.__name__)
        if args:
            fn += "; [args] {}".format(list(args))
        logging.debug(fn)
        return function(*args)

    return proceed


@show_args
def get_categories():
    """Retrieve existing categories."""
    r = requests.get(API_URL + '/categories.json', headers=headers)
    logging.debug("[{}]: {}".format(r.status_code, r.json()))

    try:
        category_list = r.json()['category_list']['categories']
        _categories = {}
        for _category in category_list:
            _categories[_category['id']] = _category['name']
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
        _topics = {}
        for _category in topic_list:
            _topics[_category['id']] = _category['title']
        return _topics

    except KeyError:
        logging.warning("response doesn't contain target keys")
        return None


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

    topics = get_topic_from_category(2)
    logging.info("topics: %s" % topics)
