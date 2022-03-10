# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os

from itemadapter import ItemAdapter

import scrapy
from scrapy.pipelines.images import ImagesPipeline

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class LmDataBasePipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.lm_2022_03_10

    def process_item(self, item, spider):
        collection = self.mongobase[spider.name]
        try:
            collection.insert_one(item)
        except DuplicateKeyError:
            pass
        return item


class LmImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['images']:
            for image in item['images']:
                try:
                    yield scrapy.Request(image)
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None, *, item=None):
        _id = item['_id']
        dir_path = f'{os.getcwd()}\\images\\{_id}\\'
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        file_name = os.path.basename(request.url)
        file_path = os.path.join(dir_path, file_name)
        return file_path

    def item_completed(self, results, item, info):
        if results:
            item['images'] = [itm[1] for itm in results if itm[0]]
        return item
