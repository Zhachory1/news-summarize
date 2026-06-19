import ipaddress
import socket
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
_ALLOWED_SCHEMES = {'http', 'https'}
_BLOCKED_NETWORKS = [
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('169.254.0.0/16'),
    ipaddress.ip_network('::1/128'),
    ipaddress.ip_network('fc00::/7'),
    ipaddress.ip_network('fe80::/10'),
]


class UrlValidationError(ValueError):
    pass


def set_flags(url_path):
    global url_path_prefix
    url_path_prefix = url_path


def validate_article_url(url):
    parsed = urlparse((url or '').strip())
    if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
        raise UrlValidationError('article_url must use http or https')
    if not parsed.hostname:
        raise UrlValidationError('article_url must include a hostname')
    if parsed.hostname.lower() in {'localhost', 'localhost.'}:
        raise UrlValidationError('article_url must not point to localhost')
    try:
        infos = socket.getaddrinfo(parsed.hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UrlValidationError(f'could not resolve article_url hostname: {parsed.hostname}') from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if any(ip in network for network in _BLOCKED_NETWORKS):
            raise UrlValidationError('article_url must not resolve to a private or local network')
    return parsed.geturl()


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
    article_url = validate_article_url(article_url)
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
        return jsonify({'error': {'code': 'missing_article_url', 'message': 'article_url is required'}}), 400
    try:
        return jsonify(extract_article_data(article_url))
    except UrlValidationError as exc:
        return jsonify({'error': {'code': 'invalid_article_url', 'message': str(exc)}}), 400
    except Exception as exc:
        return jsonify({'error': {'code': 'article_extraction_failed', 'message': str(exc)}}), 502
