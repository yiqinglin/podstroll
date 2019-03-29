from __future__ import print_function

import argparse
import logging

import feedparser
import requests
from pymongo import MongoClient

import settings


def crawl_feed_url(args):
    crawler = ShowCrawler(
        settings.MONGO_URI,
        settings.MONGO_DATABASE,
        settings.MONGO_COLLECTION,
    )
    crawler.update_feed_url()
    logging.info('All done!')


def crawl_metadata(args):
    crawler = ShowCrawler(
        settings.MONGO_URI,
        settings.MONGO_DATABASE,
        settings.MONGO_COLLECTION,
    )
    crawler.update_metadata()
    logging.info('All done!')


class ShowCrawler(object):
    def __init__(self, mongo_uri, database, collection):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[database]
        self.collection = self.db[collection]
        self.podcasts = self.collection.find({})

    def update_feed_url(self):
        logger = logging.getLogger('feed_url')
        logger.info('Updating podcast feed url...')

        for pod in self.podcasts:
            podcast_id = pod['podcast_id']
            url = settings.LOOK_UP_BASE + podcast_id

            try:
                r = requests.get(url)
                data = r.json()
                feed_url = data['results'][0].get('feedUrl', None)
                artwork = data['results'][0].get('artworkUrl600', None)

                # If podcast has no feedUrl, remove it from the db.
                if not feed_url:
                    logger.warning(
                        'Removing the podcast as it does not have feed url: %s',
                        podcast_id)
                    self.collection.delete_one({'_id': pod['_id']})
                    continue

                # If the feed url returns 404, remove it from the db.
                if requests.get(feed_url).status_code == 404:
                    logger.warning(
                        'Removing the podcast as it does not have a valid feed url: %s',
                        podcast_id)
                    self.collection.delete_one({'_id': pod['_id']})
                    continue

                # If the feed url and artwork link remain the same, continue to the next podcast.
                if feed_url == pod.get('feed_url',
                                       None) and artwork == pod.get(
                                           'feed_url', None):
                    continue

                logger.info('Updating feedUrl and artwork to podcast %s',
                            pod['podcast_id'])
                self.collection.find_one_and_update(
                    {'_id': pod['_id']},
                    {'$set': {
                        'feed_url': feed_url,
                        'artwork': artwork
                    }})
            except Exception as error:
                logger.exception(error)

    def update_metadata(self):
        logger = logging.getLogger('metadata')
        logger.info('Updating podcast details using feed url...')

        for pod in self.podcasts:
            feed_url = pod.get('feed_url', None)

            if not feed_url:
                logger.warning(
                    'Removing the podcast as it does not have feed url: %s',
                    pod['podcast_id'])
                self.collection.delete_one({'_id': pod['_id']})
                continue

            logger.debug(feed_url)
            d = feedparser.parse(feed_url)
            pod_channel = d['channel']

            website_link = pod_channel.get('link', '')
            description = pod_channel.get('description', '')
            summary = pod_channel.get('summary', '')

            pod_img = pod_channel.get('image', None)
            image = pod_img.get('url', '') if pod_img else ''
            pod_type = pod_channel.get('itunes_type', '')
            subtitle = pod_channel.get('subtitle', '')
            itunes_explicit = pod_channel.get('itunes_explicit', '')
            episode_count = len(d.entries)

            logger.info(
                'Writing into database with detailed information for podcast %s',
                pod['podcast_id'])

            self.collection.find_one_and_update({'_id': pod['_id']}, {
                '$set': {
                    'subtitle': subtitle,
                    'website_link': website_link,
                    'description': description,
                    'summary': summary,
                    'pod_type': pod_type,
                    'episode_count': episode_count,
                    'itunes_explicit': itunes_explicit,
                    'image': image
                }
            })


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Create the top-level parser
    parser = argparse.ArgumentParser(prog='show_crawler')
    subparsers = parser.add_subparsers(help='sub-command help')

    # Create the parser for the "feedurl" command
    parser_feedurl = subparsers.add_parser(
        'feed', help="Crawl shows' feed urls.")
    parser_feedurl.set_defaults(func=crawl_feed_url)

    # Create the parser for the "metadata" command
    parser_metadata = subparsers.add_parser(
        'metadata', help="Crawl shows' metadata.")
    parser_metadata.set_defaults(func=crawl_metadata)

    # Parse the args and call whatever function was selected
    args = parser.parse_args()
    args.func(args)
