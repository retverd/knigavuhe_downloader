import os
import re
from typing import List

import requests
from bs4 import BeautifulSoup

SAVE_FOLDER = './outputs'


def get_title_author(soup: BeautifulSoup) -> List[str]:
    """
    Returns book's title and author

    :param soup: page content
    :returns: list with title and author
    """
    # Get page title and replace special chars
    header = re.sub(':', '_', soup.find('title').text)
    # Title looks like '<title> (слушать аудиокнигу бесплатно) - автор <author>'
    title, _ = header.split(' (')
    _, author = header.split('автор ')
    return [title, author]


def get_track_urls(soup: BeautifulSoup) -> List[str]:
    """
    Returns list of URLs for audio tracks

    :param soup: page content
    :returns: list with URLs for audio tracks
    """
    script_with_mp3 = None

    # Iterate over <script>s and find the right one
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string is not None and script.string.find("mp3") != -1:
            script_with_mp3 = script.string

    if script_with_mp3 is None:
        raise Exception('Track URLs were not found!')

    # Find all URLs with mp3s
    results = re.findall('https:.*?mp3', script_with_mp3)

    track_urls = []
    for result in results:
        if not result.endswith(r'\/0.mp3'):
            track_urls.append(result.replace('\\', ''))

    if len(track_urls) == 0:
        raise Exception('Track URLs were not found!')

    return track_urls


def main():
    url = input("Enter URL for book to be downloaded: ")

    book_page = requests.get(url)
    soup = BeautifulSoup(book_page.content, 'html.parser')
    # Get book metadata
    title, author = get_title_author(soup)
    print(f'Downloading: {author} - "{title}"')
    # Get list of URLs for audio tracks
    track_urls = get_track_urls(soup)

    # Create folder for author if required
    if not os.path.exists(f'{SAVE_FOLDER}/{author}'):
        os.makedirs(f'{SAVE_FOLDER}/{author}')
    # Create folder for book if required
    if not os.path.exists(f'{SAVE_FOLDER}/{author}/{title}'):
        os.makedirs(f'{SAVE_FOLDER}/{author}/{title}')

    # Iterate over track URLs and save files to specified folder
    i = 1
    total_len = len(track_urls)
    for track in track_urls:
        r = requests.get(track, allow_redirects=True)
        open(f'{SAVE_FOLDER}/{author}/{title}/{i:03}.mp3', 'wb').write(r.content)
        print(f'Progress: {i*100/total_len:6.2f}%')
        i += 1


if __name__ == '__main__':
    main()
