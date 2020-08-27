import inspect
import logging
import os
import sys

import requests


def get_categories():
    """Retrieve existing categories."""
    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)
    fn = inspect.getframeinfo(frame)[2]
    logging.debug("[fn] %s()", fn)
    for i in args:
        logging.debug("[arg] %s = %s", i, values[i])

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

