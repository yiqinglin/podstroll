import logging
from collections import Counter
from time import mktime
from datetime import datetime

import feedparser
from pymongo import MongoClient

import settings


def main():
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DATABASE]
    pod_collection = db[settings.PODCAST_COLLECTION]
    episode_collection = db[settings.EPISODE_COLLECTION]
    podcasts = pod_collection.find({})

    for pod in podcasts:
        feed_url = pod.get('feed_url', None)
        if not feed_url:
            continue

        try:
            d = feedparser.parse(feed_url)

            if len(d.entries) < 1:
                continue
            for episode in d.entries:
                link = episode.get('link', '')
                episodeContent = {'podcast_id': pod['podcast_id']}
                for key, value in episode.iteritems():
                    if key == 'published_parsed':
                        value = datetime.fromtimestamp(mktime(value))
                    episodeContent[key] = value
                episode_collection.find_one_and_update(
                    {'link': link}, {'$set': episodeContent}, upsert=True)
                logging.info('finished updating episode:%s', link)
            logging.info('finished updating all episodes from podcast:%s',
                         feed_url)
        except Exception as error:
            logging.exception(error)
    logging.info('all done!')


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    main()
