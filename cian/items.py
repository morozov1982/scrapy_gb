# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Compose


def clear_price(value):
    value = value.replace('\xa0', '').replace('₽', '')
    try:
        return int(value)
    except:
        return value


def change_url(value):
    return value.replace('-2.', '-1.')


class CianItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst)
    price = scrapy.Field(output_processor=TakeFirst,
                         input_processor=MapCompose(clear_price))
    photos = scrapy.Field(input_processor=MapCompose(change_url))
