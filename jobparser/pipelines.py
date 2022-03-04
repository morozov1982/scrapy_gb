# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancies_2022_03_04

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['_id'] = item['url'].split('?')[0].split('/')[-1]
            item['salary_from'], item['salary_to'], item[
                'currency'] = self.process_hh_salary(item['salary'])
        elif spider.name == 'superjobru':
            item['_id'] = item['url'].split('-')[-1].split('.')[0]
            item['salary_from'], item['salary_to'], item[
                'currency'] = self.process_sj_salary(item['salary'])

        del item['salary']

        collection = self.mongobase[spider.name]
        try:
            collection.insert_one(item)
        except DuplicateKeyError:
            # устал читать в консоли ;-)
            # print('Такая запись уже есть в БД')
            pass

        return item

    def process_hh_salary(self, salary):
        data_from = None
        data_to = None
        data_currency = None

        for idx, val in enumerate(salary):
            if val.strip() == 'от':
                data_from = salary[idx+1]
            if val.strip() == 'до':
                data_to = salary[idx+1]

        if data_from or data_to:
            data_currency = salary[-2]

        return data_from, data_to, data_currency

    def process_sj_salary(self, salary):
        salary = [i for i in salary if not i.isspace()]

        data_from = None
        data_to = None
        data_currency = None

        for idx, val in enumerate(salary):
            if val == '—':
                data_from = salary[idx-1]
                data_to = salary[idx+1]
                data_currency = salary[idx+2]
            elif val.strip() == 'от':
                data = salary[idx+1].split()
                data_currency = data.pop()
                data_from = ' '.join(data)
            elif val.strip() == 'до':
                data = salary[idx+1].split()
                data_currency = data.pop()
                data_to = ' '.join(data)

        return data_from, data_to, data_currency
