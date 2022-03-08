import scrapy
from scrapy.http import HtmlResponse
from olxparser.items import OlxparserItem
from scrapy.loader import ItemLoader


class OlxSpider(scrapy.Spider):
    name = 'olx'
    allowed_domains = ['olx.kz']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [
            f'https://www.olx.kz/alma-ata/q-{kwargs.get("search")}/']

    def parse(self, response: HtmlResponse):
        links = response.xpath('//a[@data-cy="listing-ad-title"]')
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=OlxparserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price',
                         '//div[@data-testid="ad-price-container"]/h3/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('photos',
                         '//img[contains(@data-testid, "swiper-image")]/@src | //img[contains(@data-testid, "swiper-image")]/@data-src')

        yield loader.load_item()

        # name = response.xpath('//h1/text()').get()
        # price = response.xpath(
        #     '//div[@data-testid="ad-price-container"]/h3/text()').getall()
        # url = response.url
        # photos = response.xpath(
        #     '//img[contains(@data-testid, "swiper-image")]/@src | '
        #     '//img[contains(@data-testid, "swiper-image")]/@data-src').getall()
        #
        # yield OlxparserItem(name=name, price=price, url=url, photos=photos)
