from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

import nltk
from newspaper import Article
from textblob import TextBlob

news_summarize = Blueprint('news_summarize', __name__, url_prefix='/')
url_path_prefix = '/'
_ARTICLE_CACHE = {}
_TRACKING_PARAMS = {'fbclid', 'gclid', 'mc_cid', 'mc_eid'}


def set_flags(url_path):
    global url_path_prefix
    url_path_prefix = url_path


def normalize_url(url):
    parsed = urlparse((url or '').strip())
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith('utm_') and key.lower() not in _TRACKING_PARAMS
    ]
    path = parsed.path.rstrip('/') or '/'
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, '', urlencode(sorted(query)), ''))


def ensure_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)


def clear_article_cache():
    _ARTICLE_CACHE.clear()


def extract_article_data(article_url, article_cls=None):
    cache_key = normalize_url(article_url)
    if cache_key in _ARTICLE_CACHE:
        return _ARTICLE_CACHE[cache_key]

    ensure_nltk_data()
    article_cls = article_cls or Article
    article = article_cls(article_url)
    article.download()
    article.parse()
    article.nlp()
    analysis = TextBlob(article.text)
    data = {
        'title': article.title,
        'authors': article.authors,
        'pub_date': article.publish_date,
        'keywords': article.keywords,
        'summary': article.summary,
        'polarity': analysis.polarity,
    }
    _ARTICLE_CACHE[cache_key] = data
    return data

@news_summarize.get('/')
def index():
    return render_template('index.html', url_prefix=url_path_prefix)

@news_summarize.post('/summarize')
def summarize():
    payload = request.get_json(silent=True) or {}
    article_url = payload.get('article_url')
    if not article_url:
        return jsonify({'error': 'article_url is required'}), 400
    return jsonify(extract_article_data(article_url))
