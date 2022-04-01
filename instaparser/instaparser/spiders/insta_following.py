import json
import re
from copy import deepcopy
from urllib.parse import urlencode

import scrapy
from scrapy.http import HtmlResponse

from instaparser.items import InstaFollowersItem


class InstaFollowingSpider(scrapy.Spider):
    name = 'insta_following'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    insta_login = 'deep_stupidity'
    insta_password = '#PWD_INSTAGRAM_BROWSER:10:1648789480:AXpQAB+/i+XMmPBiLXqxCClhpkMyUe6eCwJtzKRXblsoHwEp0pY+EijQxt4mJ+0NAsRh7eOUnruOjODpQ5R9bRiDchh3E4VjUEfP6V5DrRU00CVnctABLNFUiH2QH9U4jgRzZ0bX9EpHYtgB1iofnw=='
    user_for_parse = 'papa_morozov'  # 'techskills_2022'
    api_url = 'https://i.instagram.com/api/v1/friendships/'

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
            yield response.follow(f'/{self.user_for_parse}',
                                  callback=self.friends_parse,
                                  cb_kwargs={'username': self.user_for_parse})

    def friends_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'count': 12}
        url_friends = f'{self.api_url}{user_id}/following/?{urlencode(variables)}'

        yield response.follow(
            url_friends,
            callback=self.user_following_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)},
            headers={'User-Agent': 'Instagram 155.0.0.37.107'}
        )

    def user_following_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()

        if j_data.get('big_list'):
            variables['max_id'] = j_data.get('next_max_id')
            url_followers = f'{self.api_url}{user_id}/followers/?{urlencode(variables)}'

            yield response.follow(
                url_followers,
                callback=self.user_following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)},
                headers={'User-Agent': 'Instagram 155.0.0.37.107'}
            )

        following = j_data.get('users')

        for follow in following:
            __id = f'{str(follow.get("pk"))}_{user_id}'

            item = InstaFollowersItem(
                _id=__id,
                user_id=user_id,
                username=username,
                friend_id=follow.get('pk'),
                friend_username=follow.get('username'),
                friend_pic_url=follow.get('profile_pic_url'),
                friend_full_name=follow.get('full_name'),
                friend_data=follow,
            )
            yield item

    def fetch_csrf_token(self, text):
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
