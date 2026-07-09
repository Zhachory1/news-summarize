import unittest
from unittest.mock import patch

try:
    from flask import Flask
    from src.news_summarize import (
        clear_article_cache,
        extract_article_data,
        news_summarize,
        normalize_url,
        set_flags,
        validate_article_url,
        UrlValidationError,
    )
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(f'project runtime dependency missing: {exc.name}') from exc


class FakeArticle:
    calls = 0

    def __init__(self, url):
        self.url = url
        self.text = 'Good useful article text.'
        self.title = 'Useful article'
        self.authors = ['Reporter']
        self.publish_date = '2026-06-19'
        self.keywords = ['news']
        self.summary = 'Useful summary'

    def download(self):
        FakeArticle.calls += 1

    def parse(self):
        pass

    def nlp(self):
        pass


class NewsSummarizeTests(unittest.TestCase):
    def setUp(self):
        clear_article_cache()
        set_flags('/')
        FakeArticle.calls = 0

    def app(self):
        app = Flask(__name__, template_folder='../src/templates')
        app.register_blueprint(news_summarize)
        return app

    def test_normalize_url_removes_tracking_and_fragment(self):
        first = normalize_url('https://Example.com/story/?utm_source=x&id=7#section')
        second = normalize_url('https://example.com/story?id=7')

        self.assertEqual(first, second)

    def test_extract_article_data_caches_by_normalized_url(self):
        with patch('src.news_summarize.ensure_nltk_data'), patch(
            'src.news_summarize.socket.getaddrinfo',
            return_value=[(None, None, None, None, ('93.184.216.34', 0))],
        ):
            first = extract_article_data(
                'https://example.com/story?id=7&utm_source=x',
                article_cls=FakeArticle,
            )
            second = extract_article_data(
                'https://example.com/story/?id=7#fragment',
                article_cls=FakeArticle,
            )

        self.assertEqual(first, second)
        self.assertEqual(FakeArticle.calls, 1)

    def test_index_route_renders(self):
        response = self.app().test_client().get('/')

        self.assertEqual(response.status_code, 200)

    def test_index_route_uses_normalized_url_prefix_for_frontend_urls(self):
        set_flags('news')

        response = self.app().test_client().get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'href="/news/static/favicon.ico"', response.data)
        self.assertIn(b'const summarizeUrl = "/news/summarize";', response.data)
        self.assertIn(b'src="/news/static/loading-gif.gif"', response.data)

    def test_summarize_requires_article_url(self):
        response = self.app().test_client().post('/summarize', json={})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error']['code'], 'missing_article_url')

    def test_validate_article_url_blocks_localhost(self):
        with self.assertRaises(UrlValidationError):
            validate_article_url('http://localhost:8000/story')

    def test_summarize_route_returns_structured_url_error(self):
        response = self.app().test_client().post('/summarize', json={'article_url': 'file:///etc/passwd'})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error']['code'], 'invalid_article_url')

    def test_summarize_route_returns_missing_nltk_data_error(self):
        with patch('src.news_summarize.extract_article_data', side_effect=NltkDataError('install punkt')):
            response = self.app().test_client().post(
                '/summarize',
                json={'article_url': 'https://example.com/story'},
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json()['error']['code'], 'missing_nltk_data')

    def test_summarize_route_returns_extracted_data(self):
        with patch('src.news_summarize.extract_article_data', return_value={'title': 'T'}):
            response = self.app().test_client().post(
                '/summarize',
                json={'article_url': 'https://example.com/story'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'title': 'T'})


if __name__ == '__main__':
    unittest.main()
