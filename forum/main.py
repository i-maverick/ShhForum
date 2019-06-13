import logging
import os

from aiohttp import web
from aiohttp.web import normalize_path_middleware
from aiohttp_security import setup as setup_security, SessionIdentityPolicy
from aiohttp_session import SimpleCookieStorage, session_middleware
from aiohttp_swagger import *
import sentry_sdk

from forum.db import init_db
from forum.db_auth import DBAuthorizationPolicy
from forum.routes import setup_routes
from forum.settings import load_config, BASE_DIR


log = logging.getLogger(__name__)


async def init_app(config):

    middlewares = [
        normalize_path_middleware(append_slash=False, remove_slash=True),
        # This storage is only for testing! Cannot be used on production!!!
        session_middleware(SimpleCookieStorage())
    ]
    app = web.Application(middlewares=middlewares)

    app['config'] = config
    setup_routes(app)

    swagger_filepath = os.path.join(BASE_DIR, 'docs', 'swagger.yaml')
    setup_swagger(app, swagger_from_file=swagger_filepath)

    db_pool = await init_db(app)

    setup_security(app, SessionIdentityPolicy(),
                   DBAuthorizationPolicy(db_pool))

    log.debug(app['config'])

    return app


def main(configpath):
    config = load_config(configpath)
    logging.basicConfig(level=logging.DEBUG)
    # SENTRY_KEY has a fake value in config
    sentry_sdk.init(config['sentry']['SENTRY_KEY'])
    app = init_app(config)
    web.run_app(app)


# if __name__ == '__main__':
#     import argparse
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-c", "--config", help="Provide path to config file")
#     args = parser.parse_args()
#
#     if args.config:
#         main(args.config)
#     else:
#         parser.print_help()
