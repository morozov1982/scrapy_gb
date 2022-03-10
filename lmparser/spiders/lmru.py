import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from lmparser.items import LmparserItem


class LmruSpider(scrapy.Spider):
    name = 'lmru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [
            f'https://leroymerlin.ru/catalogue/{kwargs.get("category")}/']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath(
            '//div[@aria-label="Pagination"]'
            '//a[@data-qa-pagination-item="right"]/@href').extract_first()
        yield response.follow(next_page, callback=self.parse)

        print()

        ads_links = response.xpath('//div[@data-qa-product]/a/@href').extract()

        for link in ads_links:
            yield response.follow(link, callback=self.ads_parse)

    def ads_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=LmparserItem(), response=response)
        loader.add_xpath('_id', '//span[@slot="article"]/@content')
        loader.add_xpath('name', '//h1/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//uc-pdp-price-view[@slot="primary-price"]//span[@slot="price"]/text()')
        # loader.add_xpath('images', '//picture[@slot="pictures"]/source[1]/@srcset')  # если надо покрупнее
        loader.add_xpath('images', '//picture[@slot="pictures"]/img/@src')

        yield loader.load_item()
