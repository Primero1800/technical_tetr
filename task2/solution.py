"""
Содержимое страниц русскоязычной википедии оказалось довольно грязным.
Так Японский журавль оказался в букве Ж вместо Я
Выполняя задание, так как это не указано в деталях, пришлось ориаентироваться на то,
что из-за этих записей-паразитов придется проверять каждую строку, а не добавлять все скопом при
условии, что первая и последняя запись начинаются с одной буквы.
Так же было сделано допущение, что эти животные-паразиты из неродных отделов не дублируются в своей
родной букве.
Так же принято условие, что в задании все-таки имелись ввиду животные, которые начинаются с букв кирриллицы, а
не латинских. Хотя они тоже присутствуют в русскоязычной википедии.
Отдельно буква Ё встречается в неродных разделах, но своего раздела с буквой Ё нет. Поэтому результаты буквы Ё,
набранные исключительно за счет животных-паразитов, учтены совместо с буквой Е
"""

import asyncio
import csv
import logging

import bs4
from httpx import Response, AsyncClient

LETTERS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ"
START_URL = ('https://ru.wikipedia.org/w/index.php?title=%D0%9A%D0%B0%D1%82%'
             'D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%96%D0%B8%D0%B2%D0'
             '%BE%D1%82%D0%BD%D1%8B%D0%B5_%D0%BF%D0%BE_%D0%B0%D0%BB%D1'
             '%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83&from=')

LOGGER = logging.getLogger(__name__)
FILE_NAME = "beasts.csv"

LOGGER.setLevel(logging.INFO)
if not LOGGER.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    LOGGER.addHandler(console_handler)


class Parser:
    def __init__(
            self,
            file: str,
            start_url: str
    ):
        self.file = file
        self.start_url = start_url
        self.counter = {}

    async def write_result(self):
        with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in sorted(self.counter.items(), key=lambda x: x[0]):
                writer.writerow(row)

    async def process_results(self, results: tuple):
        for result in results:
            for key, value in result.counter.items():
                if key in LETTERS:
                    self.counter.setdefault(key, 0)
                    self.counter[key] += value
        if "Ё" in self.counter:
            self.counter.setdefault('Е', 0)
            self.counter['Е'] += self.counter['Ё']
            del self.counter['Ё']

    async def start(self):
        workers = [Worker(
            start_url=f"{self.start_url}{letter}",
            target=letter,
        ) for letter in LETTERS]

        tasks = [asyncio.create_task(worker.start()) for worker in workers]
        [task.add_done_callback(Worker.callback_report) for task in tasks]

        results = await asyncio.gather(*tasks)

        await self.process_results(results)
        await self.write_result()


class Worker:
    def __init__(
            self,
            start_url: str,
            target: str,
            logger: logging.Logger = LOGGER
    ):
        self.next_page = start_url
        self.target = target
        self.logger = logger
        self.page_counter = 0
        self.counter = {}

    async def start(self):
        while self.next_page:
            await self.parse_next()
        self.logger.debug("Parser task completed. Writting result")

        return self

    @staticmethod
    def callback_report(task):
        result = task.result()
        result.logger.info("Worker %r finished with result: %s" % (result.target, result.counter))

    async def parse_next(self):
        self.page_counter += 1
        self.logger.debug("Parsing %s page" % self.page_counter)
        async with AsyncClient() as client:
            response: Response = await client.get(url=self.next_page)
            soup = bs4.BeautifulSoup(response.text, 'html.parser')

            next_page = await self.get_next_page(soup=soup)
            self.next_page = response.url.join(next_page) if next_page else None
            self.logger.debug("Next page found: %s" % self.next_page)

            beasts = await self.get_beasts(soup=soup)
            await self.count_beasts(beasts)

    async def get_next_page(self, soup: bs4.BeautifulSoup):

        mw_pages_div = soup.find('div', id='mw-pages')
        if not mw_pages_div:
            return None
        next_page_link = mw_pages_div.find('a', string='Следующая страница')
        if not next_page_link:
            return None

        return next_page_link.get('href')

    async def get_beasts(self, soup: bs4.BeautifulSoup):
        beasts = []
        mw_category_div = soup.find('div', class_='mw-category mw-category-columns')
        if mw_category_div:
            h3_tags = mw_category_div.find_all('h3')

            if not h3_tags:
                return beasts

            start_h3 = h3_tags[0]
            end_h3 = h3_tags[1] if len(h3_tags) > 1 else None

            current_element = start_h3.find_next_sibling()
            while current_element and current_element != end_h3:
                if current_element.name == 'ul':
                    li_tags = current_element.find_all('li')
                    for li_tag in li_tags:
                        beasts.append(li_tag.text.strip())
                current_element = current_element.find_next_sibling()
        return beasts

    async def count_beasts(self, beasts: list[str]):
        if not beasts or beasts[0][0] != self.target:
            self.next_page = None
            return

        for beast in beasts:
            self.counter.setdefault(beast[0], 0)
            self.counter[beast[0]] += 1


if __name__ == "__main__":
    parser = Parser(
        file=FILE_NAME,
        start_url=START_URL,
    )

    asyncio.run(parser.start())
