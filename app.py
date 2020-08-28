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


@show_args
def delete_topic(_id):
    """Delete a topic with a target ID."""
    r = requests.delete(API_URL + "/t/{}.json".format(_id), headers=headers)
    logging.debug("[{}] {}".format(r.status_code, r.text))


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stdout,
        level=logging.DEBUG)

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
    # categories = {1: 'Uncategorized', 3: 'Staff', 4: 'Lounge', 2: 'Site Feedback'}
    logging.info("categories: %s" % categories)

    topics = get_topic_from_category(3)
    # topics = {2: 'About the Staff category', 9: 'READ ME FIRST: Admin Quick Start Guide', 6: 'Privacy Policy',
    #           5: 'FAQ/Guidelines', 4: 'Terms of Service'}
    logging.info("topics: %s" % topics)
