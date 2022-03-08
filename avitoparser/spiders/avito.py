from avitoparser.items import AvitoparserItem

import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']

    def __init__(self, mark, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = \
            [f'https://www.avito.ru/rossiya/bytovaya_elektronika?q={mark}']

    def parse(self, response: HtmlResponse):
        ads_links = response.xpath(
            '//a[@data-marker="item-title"]/@href').extract()
        for link in ads_links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        name = response.css(
            'h1.title-info-title span.title-info-title-text').extract_first()
        photos = response.xpath(
            '//div[contains(@class, "gallery-img-wrapper")]'
            '//div[contains(@class, "gallery-img-frame")]/@data-url').extract()
        price = response.xpath(
            '//span[@class="js-item-price"][1]/text()').extract()

        yield AvitoparserItem(name=name, photos=photos, price=price)
        print(name, photos, price)
