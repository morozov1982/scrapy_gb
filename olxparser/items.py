# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Compose


def fix_price(price_list):
    try:
        result = int(price_list[0].replace(' ', ''))
        return [result, price_list[-1]]
    except:
        return price_list


class OlxparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=Compose(fix_price))
    photos = scrapy.Field()


# class OlxparserItem(scrapy.Item):
#     # define the fields for your item here like:
#     _id = scrapy.Field()
#     name = scrapy.Field()
#     url = scrapy.Field()
#     price = scrapy.Field()
#     photos = scrapy.Field()
