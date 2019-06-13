from setuptools import setup


install_requires = [
    'aiohttp',
    'bcrypt',
    'pytoml',
    'aiohttp_security[session]',
    'sqlalchemy',
    'asyncpg',
    'asyncpgsa',
]

setup(
    name='ShhForum',
    version='0.1.0',
    install_requires=install_requires,
)
