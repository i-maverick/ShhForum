import os
import pathlib
import pytoml as toml

BASE_DIR = pathlib.Path(__file__).parent.parent


def load_config(path):
    print(os.getcwd())
    with open(path) as f:
        conf = toml.load(f)
    return conf
