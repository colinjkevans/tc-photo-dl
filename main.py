import requests
import os
import shutil
from bs4 import BeautifulSoup


LOGIN_URL = 'https://www.transparentclassroom.com/souls/sign_in?locale=en'
ALBUM_URL = 'https://www.transparentclassroom.com/s/144/children/{}/pictures?locale=en'
URL_ROOT = 'https://www.transparentclassroom.com{}'
PICTURES_SUFFIX = '/pictures'

user = 'username'
password = 'password'


def download_image(child, url, description):
    filename = '.'.join(url.split('/')[-1].split('.')[:-1])
    print(filename)
    img_path = os.path.join(child, filename + '.jpg')
    txt_path = os.path.join(child, filename + '.txt')
    print(img_path, txt_path)

    img_r = requests.get(url, stream=True)
    if img_r.status_code == 200:
        with open(img_path, 'wb') as f:
            img_r.raw.decode_content = True
            shutil.copyfileobj(img_r.raw, f)
        with open(txt_path, 'w') as f:
            f.write(description)
    else:
        print('Failed {}'.format(url))


def get_child_links(html):
    soup = BeautifulSoup(html, "html.parser")

    child_links = soup.find_all('a', {'id': 'child-nav'})

    return {link['title']: link['href'].split('?')[0] for link in child_links}


def process_album(child, url):
    image_urls_descriptions = []
    page_url = url
    while True:
        print('Album page:', page_url, end=': ')
        page_r = session.get(page_url)
        image_urls_descriptions += get_album_page_image_urls(page_r.text)
        page_soup = BeautifulSoup(page_r.text, "html.parser")
        next_page = page_soup.find('a', {'class': 'next_page'})
        if next_page is None:
            break
        else:
            page_url = URL_ROOT.format(next_page['href'])

    print(child, 'images:', len(image_urls_descriptions))

    # Download the images
    if not os.path.isdir(child):
        os.mkdir(child)
    for image_url, image_description in image_urls_descriptions:
        download_image(child, image_url, image_description)


def get_album_page_image_urls(html):
    page_image_urls_descriptions = []
    page_soup = BeautifulSoup(html, "html.parser")
    for link in page_soup.find_all('a', {'data-fancybox-group': 'gallery'}):
        page_image_urls_descriptions.append([link['data-original'], link['title']])

    print(len(page_image_urls_descriptions))
    return page_image_urls_descriptions



# Main
session = requests.Session()

# Get auth token for login from login page
r = session.get(LOGIN_URL)
soup = BeautifulSoup(r.text, "html.parser")

inputs = {form_input.get('name'): form_input.get('value') for form_input in soup.find_all('input')}
inputs['soul[login]'] = user
inputs['soul[password]'] = password

# Use username, password and auth token for login
post_data = inputs

r = session.post(LOGIN_URL, post_data)
child_links = get_child_links(r.text)

album_urls = {}
for child in child_links:
    album_urls[child] = URL_ROOT.format(child_links[child])+PICTURES_SUFFIX

for child, url in album_urls.items():
    print(child)
    process_album(child, url)

