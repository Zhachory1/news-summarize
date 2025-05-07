from src import create_app
from src.news_summarize import set_flags

from absl import app
from absl import flags
from absl import logging

FLAGS = flags.FLAGS

flags.DEFINE_string('url_path', '/', 'Prefix of URL path this flask app is at. Useful for proxy_passes')
flags.DEFINE_enum('env', 'prod', ['prod', 'dev', 'test'], 'Type of env we want this binary to be in.')
flags.DEFINE_integer('port', 8080, 'The port that the app will connect to')

def main(argv):
    del argv  # Unused.
    logging.info('url_path is %s.', FLAGS.url_path)
    logging.info('env is %s.', FLAGS.env)
    set_flags(FLAGS.url_path)
    if FLAGS.env == 'prod':
        create_app('src.conf.ProductionConfig').run(host='0.0.0.0', port=FLAGS.port)
    elif FLAGS.env == 'dev':
        create_app('src.conf.DevelopmentConfig').run(host='0.0.0.0', port=FLAGS.port)
    else:
        create_app('src.conf.TestingConfig').run(host='0.0.0.0', port=FLAGS.port)
        

# TODO(zhach): Add flag to switch between dev, prod, and test
if __name__ == '__main__':
    app.run(main)
