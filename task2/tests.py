import pytest
from unittest.mock import AsyncMock, patch
from bs4 import BeautifulSoup

from solution import Worker, Parser


@pytest.mark.asyncio
async def test_get_next_page_returns_href():
    html = '''
    <div id="mw-pages">
        <a href="/page2">Следующая страница</a>
    </div>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    worker = Worker(start_url='http://test', target='А')
    result = await worker.get_next_page(soup)
    assert result == "/page2"


@pytest.mark.asyncio
async def test_get_next_page_none_when_no_div():
    # Нет div с id='mw-pages'
    soup = BeautifulSoup('<div></div>', 'html.parser')
    worker = Worker(start_url='http://test', target='А')
    result = await worker.get_next_page(soup)
    assert result is None


@pytest.mark.asyncio
async def test_get_beasts_correct_extraction():
    html = '''
    <div class="mw-category mw-category-columns">
        <h3>Первая буква</h3>
        <ul>
            <li>Альбатрос</li>
            <li>Аист</li>
        </ul>
        <h3>Вторая буква</h3>
    </div>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    worker = Worker(start_url='http://test', target='А')
    beasts = await worker.get_beasts(soup)
    assert 'Альбатрос' in beasts
    assert 'Аист' in beasts


@pytest.mark.asyncio
async def test_get_beasts_empty_when_structure_wrong():
    html = '<div></div>'
    soup = BeautifulSoup(html, 'html.parser')
    worker = Worker(start_url='http://test', target='А')
    beasts = await worker.get_beasts(soup)
    assert beasts == []


@pytest.mark.asyncio
async def test_count_beasts_increments_counter():
    worker = Worker(start_url='http://test', target='А')
    beasts = ['Альбатрос', 'Аист', 'Акула']
    await worker.count_beasts(beasts)
    assert worker.counter['А'] == 3


@pytest.mark.asyncio
async def test_process_results_merges_counters():
    parser = Parser(file='test.csv', start_url='http://test')

    class DummyResult:
        def __init__(self):
            self.counter = {'А': 2, 'Б': 3}

        def __getitem__(self, item):
            return self.counter[item]

        def items(self):
            return self.counter.items()

    result1 = DummyResult()
    result2 = DummyResult()
    parser.counter = {}
    await parser.process_results((result1, result2))

    assert parser.counter['А'] == 4
    assert parser.counter['Б'] == 6


@pytest.mark.asyncio
async def test_write_result_writes_csv(tmp_path):
    parser = Parser(file='test.csv', start_url='http://test')
    worker = Worker(start_url='http://test', target='А')
    worker.counter = {'А': 1, 'Б': 2, 'Ё': 3}

    await parser.process_results((worker,))
    await parser.write_result()

    with open('output.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    assert any('А' in line for line in lines)
    assert any('Б' in line for line in lines)

    assert not any('Ё' in line for line in lines)
    assert any('Е' in line for line in lines)


@pytest.mark.asyncio
async def test_worker_parse_next_with_mocked_client():
    with patch('solution.AsyncClient') as mock_client_cls:
        mock_client = mock_client_cls.return_value.__aenter__.return_value
        mock_response = AsyncMock()
        mock_response.text = '<div id="mw-pages"></div>'
        mock_response.url = 'http://test'
        mock_response.get.return_value = mock_response
        mock_client.get = AsyncMock(return_value=mock_response)

        worker = Worker(start_url='http://test', target='А')

        worker.next_page = 'http://test'
        await worker.parse_next()

        mock_client.get.assert_awaited_with(url='http://test')
