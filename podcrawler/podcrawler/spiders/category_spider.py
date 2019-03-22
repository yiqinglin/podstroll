import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
from podcrawler.items import TopCategoryItem, SubGenreItem


class CategorySpider(scrapy.Spider):
    name = "categories"

    start_urls = ["https://itunes.apple.com/us/genre/podcasts/id26"]

    custom_settings = {
        'ITEM_PIPELINES': {
            'podcrawler.pipelines.CategoryPipeline': 400
        }
    }

    def parse(self, response):
        #yield Request('http://itunes.apple.com/us/genre/podcasts-business/id1321', callback=self.parseLinks)
        hxs = Selector(response)

        # Top level categories
        anchors = hxs.xpath('//a[contains(@class,"top-level-genre")]')
        for anchor in anchors:
            itunes_id = anchor.xpath('@href').get().split('/')[-1].split(
                '?')[0][2:]
            title = anchor.xpath('text()').get()

            item = TopCategoryItem(itunes_id=itunes_id, title=title)
            yield item

        # Subgenres
        subgenre_anchors = hxs.xpath(
            '//ul[contains(@class,"top-level-subgenres")]/li/a')
        for anchor in subgenre_anchors:
            itunes_id = anchor.xpath('@href').get().split('/')[-1].split(
                '?')[0][2:]
            title = anchor.xpath('text()').get()
            parent_category = anchor.xpath('../../../a/text()').get()

            item = SubGenreItem(
                itunes_id=itunes_id,
                title=title,
                parent_category=parent_category)
            yield item