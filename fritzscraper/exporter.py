import argparse
import logging

from wsgiref.simple_server import make_server

from prometheus_client.exposition import make_wsgi_app
from prometheus_client.registry import REGISTRY

from fritzscraper.collector import FRITZBoxCollector

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("listenPort")
    parser.add_argument("host")
    parser.add_argument("user")
    parser.add_argument("password")

    args = parser.parse_args()
    collector = FRITZBoxCollector(args.host, args.user, args.password)
    REGISTRY.register(collector)

    app = make_wsgi_app()
    httpd = make_server('', int(args.listenPort), app)

    logger.info('FRITZ!Box Collector started')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('FRITZ!Box Collector terminated')


if __name__ == '__main__':
    main()
