import re
import sys
import asyncio
import aiohttp

from typing import List

from aiohttp import InvalidURL
from bs4 import BeautifulSoup

EXTRACT_TAGS = ["script", "link", "svg", "img", "meta", "style"]


def find_numbers_in_text(text: str) -> List[str]:
    numbers = re.findall(
        r'((\+7|8)(\s|\(|\)|-){,2}(\d{3})|)(\s|\(|\)|-){,2}(\d{3}(\s|\(|\)|-){,2}\d{2}(\s|\(|\)|-){,2}\d{2})', text)

    for i, number in enumerate(numbers):
        numbers[i] = ''.join(['8', number[3] or '495', re.sub(r"\D", "", number[5])])

    return numbers


def parse_html_numbers(html: str) -> List[str]:
    soup = BeautifulSoup(html, 'html.parser')

    numbers = set()

    for tag in soup.find_all():
        if tag.name in EXTRACT_TAGS:
            tag.extract()
        else:
            for val in list(tag.attrs):
                if tag.name == 'a' and val == 'href' and tag.attrs['href'][:3] == "tel":
                    continue
                del tag.attrs[val]

    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href and href.find('tel:') > -1:
            numbers.update(find_numbers_in_text(href))

    numbers.update(find_numbers_in_text(str(soup)))

    return list(numbers)


async def parser(url: str) -> (str, List[str]):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                return url, parse_html_numbers(html)
    except InvalidURL:
        sys.stderr.write(f'{url} not valid url\n\n')
        return None


async def main(urls: List[str]) -> tuple:
    tasks = map(lambda url: asyncio.create_task(parser(url)), urls)
    return await asyncio.gather(*tasks)


if __name__ == '__main__':
    lines = sys.stdin.readlines()
    _urls = list(set(filter(lambda x: x, map(str.strip, lines))))

    results = asyncio.run(main(_urls))

    for result in results:
        if result is None:
            continue
        url, parsed_numbers = result
        sys.stdout.writelines([url + ':', '\n', ', '.join(parsed_numbers), '\n\n'])
