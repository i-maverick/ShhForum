from sqlalchemy import create_engine, MetaData

from forum.db import construct_db_url
from forum.models import user, topic, thread, message
from forum.security import generate_password_hash
from forum.settings import load_config


def setup_db(executor_config=None, target_config=None):
    engine = get_engine(executor_config)

    db_name = target_config['DB_NAME']
    db_user = target_config['DB_USER']
    db_pass = target_config['DB_PASS']

    with engine.connect() as conn:
        teardown_db(executor_config=executor_config,
                    target_config=target_config)

        conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
        conn.execute("CREATE DATABASE %s" % db_name)
        conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                     (db_name, db_user))


def teardown_db(executor_config=None, target_config=None):
    engine = get_engine(executor_config)

    db_name = target_config['DB_NAME']
    db_user = target_config['DB_USER']

    with engine.connect() as conn:
        # terminate all connections to be able to drop database
        conn.execute("""
          SELECT pg_terminate_backend(pg_stat_activity.pid)
          FROM pg_stat_activity
          WHERE pg_stat_activity.datname = '%s'
            AND pid <> pg_backend_pid();""" % db_name)
        conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
        conn.execute("DROP ROLE IF EXISTS %s" % db_user)


def get_engine(db_config):
    db_url = construct_db_url(db_config)
    engine = create_engine(db_url, isolation_level='AUTOCOMMIT')
    return engine


def create_tables(target_config=None):
    engine = get_engine(target_config)

    meta = MetaData()
    meta.create_all(bind=engine, tables=[user, topic, thread, message])


def drop_tables(target_config=None):
    engine = get_engine(target_config)

    meta = MetaData()
    meta.drop_all(bind=engine, tables=[user, topic, thread, message])


def create_sample_data(target_config=None):
    engine = get_engine(target_config)

    with engine.connect() as conn:
        conn.execute(user.insert(), [
            {
                'username': 'admin',
                'password_hash': generate_password_hash('admin'),
                'superuser': True
            },
            {
                'username': 'guest',
                'password_hash': generate_password_hash('guest'),
                'superuser': False
            },
        ])
        conn.execute(topic.insert(), [
            {'name': 'Cinema'},
            {'name': 'Music'},
            {'name': 'Sport'},
        ])
        conn.execute(thread.insert(), [
            {
                'title': 'Luc Besson cinematography',
                'topic': 1,
                'created_at': '2001-01-01 00:00:00'
            },
            {
                'title': 'Madagascar movie',
                'topic': 1,
                'created_at': '2001-01-01 00:00:00'
            },
            {
                'title': 'Hard Rock music',
                'topic': 2,
                'created_at': '2001-01-01 00:00:00'
            },
            {
                'title': "You'll never walk alone!",
                'topic': 3,
                'created_at': '2001-01-01 00:00:00'
             },
        ])
        conn.execute(message.insert(), [
            {
                'content': 'Le Grand Bleu - the most wonderful movie',
                'thread': 1,
                'parent': None,
                'starter': True,
                'created_at': '2001-03-14 11:15:01',
                'updated_at': '2001-03-14 11:15:01'
            }
        ])
        conn.execute(message.insert(), [
            {
                'content': 'Yes! But Leon is the most dramatic',
                'thread': 1,
                'parent': 1,
                'starter': False,
                'created_at': '2001-03-14 11:17:12',
                'updated_at': '2001-03-14 11:17:12'
            },
            {
                'content': 'Remember the Fifth Element',
                'thread': 1,
                'parent': None,
                'starter': False,
                'created_at': '2001-03-14 11:39:21',
                'updated_at': '2001-03-14 11:39:21'
            },
            {
                'content': 'Pinguins are coming',
                'thread': 2,
                'parent': None,
                'starter': True,
                'created_at': '2001-04-21 13:12:21',
                'updated_at': '2001-04-21 13:12:21'
            },
            {
                'content': 'Hard Rock forever!',
                'thread': 3,
                'parent': None,
                'starter': True,
                'created_at': '2001-04-21 13:13:21',
                'updated_at': '2001-04-21 13:13:21'
            },
            {
                'content': 'Liverpool is the champion!!!',
                'thread': 4,
                'parent': None,
                'starter': 1,
                'created_at': '2011-06-01 23:33:21',
                'updated_at': '2011-06-01 23:33:21'
            },
        ])


if __name__ == '__main__':
    user_db_config = load_config('config/user_config.toml')['database']
    admin_db_config = load_config('config/admin_config.toml')['database']

    import argparse
    parser = argparse.ArgumentParser(description='DB related shortcuts')
    parser.add_argument("-c", "--create",
                        help="Create empty database and user with permissions",
                        action='store_true')
    parser.add_argument("-d", "--drop",
                        help="Drop database and user role",
                        action='store_true')
    parser.add_argument("-r", "--recreate",
                        help="Drop and recreate database and user",
                        action='store_true')
    parser.add_argument("-a", "--all",
                        help="Create sample data",
                        action='store_true')
    args = parser.parse_args()

    if args.create:
        setup_db(executor_config=admin_db_config,
                 target_config=user_db_config)
    elif args.drop:
        teardown_db(executor_config=admin_db_config,
                    target_config=user_db_config)
    elif args.recreate:
        teardown_db(executor_config=admin_db_config,
                    target_config=user_db_config)
        setup_db(executor_config=admin_db_config,
                 target_config=user_db_config)
    elif args.all:
        teardown_db(executor_config=admin_db_config,
                    target_config=user_db_config)
        setup_db(executor_config=admin_db_config,
                 target_config=user_db_config)
        create_tables(target_config=user_db_config)
        create_sample_data(target_config=user_db_config)
    else:
        parser.print_help()
