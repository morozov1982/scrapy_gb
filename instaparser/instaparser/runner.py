from scrapy.crawler import CrawlerProcess
import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from instaparser.spiders.insta_followers import InstaFollowersSpider
from instaparser.spiders.insta_following import InstaFollowingSpider

if __name__ == '__main__':
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    runner.crawl(InstaFollowersSpider)
    runner.crawl(InstaFollowingSpider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())

    reactor.run()
