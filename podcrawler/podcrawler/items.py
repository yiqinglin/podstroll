# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PodcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    category = scrapy.Field()
    podcast_id = scrapy.Field()


class TopCategoryItem(scrapy.Item):
    title = scrapy.Field()
    itunes_id = scrapy.Field()


class SubGenreItem(scrapy.Item):
    title = scrapy.Field()
    itunes_id = scrapy.Field()
    parent_category = scrapy.Field()