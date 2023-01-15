import os
from flask import Flask


def create_app(config_filename="src.conf.BaseConfig"):
    template_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    template_dir = os.path.join(template_dir, '__main__')
    template_dir = os.path.join(template_dir, 'src')
    template_dir = os.path.join(template_dir, 'templates')
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(config_filename)
    from src.news_summarize import news_summarize
    app.register_blueprint(news_summarize)
    return app

