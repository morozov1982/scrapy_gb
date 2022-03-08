import requests
import wget

url = 'https://frankfurt.apollo.olxcdn.com/' \
      'v1/files/gkxbwy193nya3-KZ/image;s=1200x1600'
wget.download(url, out='cat-wget.jpg')

# response = requests.get(url)

# with open('cat.jpg', 'wb') as f:
#     f.write(response.content)
