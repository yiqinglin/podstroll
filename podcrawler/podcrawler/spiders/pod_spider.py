import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
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
            podcast_id = hxs.css(
                'div#dz-report-event-url::attr(podcast-id)').get()
        except:
            podcast_id = None

        try:
            title = hxs.xpath(
                '//div[contains(@id,"title")]/div/h1/text()').get()
        except:
            title = None

        try:
            author = response.xpath('//div[@id="title"]/div/h2/text()').get()
        except:
            author = None

        try:
            category = response.xpath(
                '//li[@class="genre"]/a/span/text()').get()
        except:
            category = None

        try:
            lang = response.xpath('//li[@class="language"]/text()').get()
        except:
            lang = None

        item = PodcrawlerItem(
            title=title,
            author=author,
            category=category,
            lang=lang,
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
