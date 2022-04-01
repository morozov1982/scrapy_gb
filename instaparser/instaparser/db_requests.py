from pymongo import MongoClient

client = MongoClient('localhost', 27017)
mongo_base = client.insta_friends

followers = mongo_base['insta_followers']
following = mongo_base['insta_following']

user = input("Введи имя пользователя для поиска: ")

print('*' * 24)
print(f'\n\33[33mПодписчики {user}:\33[0m\n{"-" * 24}')
for item in followers.find({'username': user}):
    print(f'{item["friend_username"]}: {item["friend_full_name"]}')

print('*' * 25)
print(f'\n\33[33m{user} подписан на:\33[0m\n{"-" * 25}')
for item in following.find({'username': user}):
    print(f'{item["friend_username"]}: {item["friend_full_name"]}')
