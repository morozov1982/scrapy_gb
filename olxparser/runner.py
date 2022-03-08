from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from olxparser import settings
from olxparser.spiders.olx import OlxSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    search = 'котята'  # input('Что ищем?\n>>> ')
    process.crawl(OlxSpider, search=search)

    process.start()
