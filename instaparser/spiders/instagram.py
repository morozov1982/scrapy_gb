import json
import re

import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
from urllib.parse import urlencode
from copy import deepcopy


class InstaSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    insta_login = 'deep_stupidity'
    insta_password = '#PWD_INSTAGRAM_BROWSER:10:1648122368:AYJQAN4nSnFQYI3G+RDdBVZzDjuSV/K0NH+JjAfT5M9BxJwknnvq3Txijv9KwGJrxanWgDZNVB69wndCkyObi4nu2QWWtMZZnItM1VIcOdfqGeC5JagkltSgtG9nMvFd8+MTP940yQpWEL2KKspYfg=='
    parse_user = 'techskills_2022'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    query_hash = '8c2a529969ee035a5063f2fc8602a0fd'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.insta_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.insta_login,
                      'enc_password': self.insta_password},
            headers={'X-CSRFToken': csrf},
        )

    def login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body['authenticated']:
            yield response.follow(f'/{self.parse_user}',
                                  callback=self.user_parse,
                                  cb_kwargs={'username': self.parse_user})

    def user_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id,
                     'first': 12}
        url_posts = f'{self.graphql_url}query_hash={self.query_hash}&{urlencode(variables)}'

        yield response.follow(
            url_posts,
            callback=self.user_posts_parse,
            cb_kwargs={'username': username, 'user_id': user_id, 'variables': deepcopy(variables)}
        )

    def user_posts_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']

            url_posts = f'{self.graphql_url}query_hash={self.query_hash}&{urlencode(variables)}'

            yield response.follow(
                url_posts,
                callback=self.user_posts_parse,
                cb_kwargs={'username': username, 'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
        for post in posts:
            item = InstaparserItem(
                user_id=user_id,
                username=username,
                photo=post.get('node').get('display_url'),
                likes=post.get('node').get('edge_media_preview_like').get('count'),
                post_data=post.get('node')
            )
            yield item

    def fetch_csrf_token(self, text):
        """ Get csrf-token for auth """
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
