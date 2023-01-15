from flask import Blueprint
from flask import render_template
from flask import request
from flask import jsonify

import nltk
from textblob import TextBlob
from newspaper import Article

nltk.download('punkt')
news_summarize = Blueprint('news_summarize', __name__, url_prefix='/')
url_path_prefix = '/'

def set_flags(url_path):
    url_path_prefix = url_path

@news_summarize.get('/')
def index():
    return render_template('index.html', url_prefix=url_path_prefix)

@news_summarize.post('/summarize')
def summarize():
    # You grab data with the request object
    print(request.json)
    # This brings in the article information. It does not do it 
    # automatically when the instance is created.
    article = Article(request.json['article_url'])
    article.download() 
    # This allows the library to extract all the tasty information from the webpage
    # Like, authors, the text, images, date, and the title
    article.parse()
    # This allows a the fields (summary and keywords) to be extracted from the article
    article.nlp()
    # Text blob is here to help us learn about the sentiment of the article
    # This library is great for creating classifiers
    # We use Article to extract the text and then use text blob for analysis
    # > 0 => Positive
    # < 0 => Negative
    analysis = TextBlob(article.text)

    # TODO(zhach): sometimes authors include all the authors concatenated in [0]
    data = {
        'title' :   article.title,
        'authors':  article.authors,
        'pub_date': article.publish_date,
        'keywords': article.keywords,
        'summary':  article.summary,
        'polarity': analysis.polarity
    }
    return jsonify(data) 