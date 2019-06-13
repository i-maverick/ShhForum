from os import environ

from forum.main import main

DEFAULT_CONFIG = 'config/user_config.toml'

config = environ.get('FORUM_CONFIG', DEFAULT_CONFIG)

main(config)
