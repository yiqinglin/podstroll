import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
import logging
from podcrawler.items import PodcrawlerItem


class PodSpider(scrapy.Spider):
    name = "podcasts"

    start_urls = ["https://itunes.apple.com/us/genre/podcasts/id26"]
    custom_settings = {
        'ITEM_PIPELINES': {
            'podcrawler.pipelines.MongoPipeline': 400
        }
    }

    def parse(self, response):
        #yield Request('http://itunes.apple.com/us/genre/podcasts-business/id1321', callback=self.parseLinks)
        hxs = Selector(response)

        for url in hxs.xpath(
                '//a[contains(@class,"top-level-genre")]/@href').getall():
            yield Request(url, callback=self.parseLinks)

    def parsePodcast(self, response):
        hxs = Selector(response)

        try:
            canonical_link = hxs.xpath('//link[@rel="canonical"]/@href').get()
            podcast_id = canonical_link.split('/')[-1][2:]
        except:
            logging.exception('Failed to get podcast id', canonical_link)

        try:
            title = hxs.xpath(
                '//span[contains(@class, "product-header__title") and @data-test-podcast-name]/text()'
            ).get()
        except:
            title = None

        try:
            author = hxs.xpath(
                '//span[contains(@class, "podcast-header__identity") and @data-test-artist-name]/a/text()'
            ).get()
            if not author:
                author = hxs.xpath(
                    '//span[contains(@class, "podcast-header__identity") and @data-test-artist-name]/text()'
                ).get()
        except:
            author = None

        try:
            category = hxs.xpath('//li[@data-test-primary-genre]/text()').get()
        except:
            category = None

        item = PodcrawlerItem(
            title=title,
            author=author,
            category=category,
            podcast_id=podcast_id)
        yield item

    def parseLinks(self, response):
        hxs = Selector(response)
        arr = hxs.xpath(
            '//div[contains(@id,"selectedcontent")]//a/@href').getall()

        # Podcast links
        for url in arr:
            yield Request(url, callback=self.parsePodcast)

        # Alphabet links
        for url in hxs.xpath(
                '//ul[contains(@class,"list alpha")]/li/a/@href').getall():
            yield Request(url, callback=self.parseLinks)

        # Pagination links
        for url in hxs.xpath(
                '//ul[contains(@class,"list paginate")]/li/a/@href').getall():
            yield Request(url, callback=self.parseLinks)
