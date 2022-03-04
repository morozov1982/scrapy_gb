import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SuperjobruSpider(scrapy.Spider):
    name = 'superjobru'
    allowed_domains = ['superjob.ru', 'www.superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@rel="next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath(
            '//div[@class="f-test-search-result-item"]//a[contains(@href, "/vakansii/")]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        title = response.xpath('//h1//text()').get()
        salary = response.xpath('//h1/following-sibling::span//text()').getall()
        url = response.url
        yield JobparserItem(title=title, salary=salary, url=url)
