Setup
=====

Clone project into local directory::

    $ git clone https://github.com/i-maverick/ShhForum.git
    $ cd ShhForum

Create virtual environment::

    $ python3 -m venv .env

Activate virtual environment::

    $ source .env/bin/activate

Install requirements::

    $ pip install -r requirements.txt

Run PostgreSQL server::

    $ docker run --rm -d -p 5432:5432 postgres:10

Create db with tables and sample data::

    $ python db_helpers.py -a

Check db for created data::

    $ psql -h localhost -p 5432 -U postgres -d forum -c "select * from user"

Run server::

    $ python main.py -c config/user_config.toml

Swagger API::

    http://localhost:8080/api/doc


Testing
=======

Run tests::

    $ pytest .


Description
=======

Какая функциональность реализована:

- Topics: темы форума. Список - для всех.
Создание, изменение и удаление - с админскими правами.
Можно создавать вложенные темы через parent

- Threads: треды внутри тем. Список и добавление - без ограничений.
По сути тред - это лишь заголовок для списка сообщений.
При создании к треду прикрепляется стартовое сообщение (starter).

- Messages: сообщения внутри треда.
Может быть только одно стартовое сообщение (создается вместе с тредом)
Можно создавать ответы на сообщения через parent

- Авторизация и администрирование осуществляется через библиотеки
aiohttp_session и aiohttp_security.
В качестве примера используется примитивный SimpleCookieStorage,
для использования на проде его можно заменить на Redis или Memcached.

- Документирование API выполнено на основе aiohttp_swagger,
все функции описаны в файле docs/swagger.yaml.
Доступ к клиенту - по адресу http://localhost:8080/api/doc

- Для сбора ошибок используется Sentry.
Ключ SENTRY_SDK необходимо заменить на валидный.
