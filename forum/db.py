import asyncio
from datetime import datetime

import asyncpgsa

from forum.models import user, topic, thread, message


async def init_db(app):
    dsn = construct_db_url(app['config']['database'])
    pool = await asyncpgsa.create_pool(dsn=dsn)
    app['db_pool'] = pool
    return pool


def construct_db_url(config):
    DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"
    return DSN.format(
        user=config['DB_USER'],
        password=config['DB_PASS'],
        database=config['DB_NAME'],
        host=config['DB_HOST'],
        port=config['DB_PORT'],
    )


async def get_user_by_name(conn, username):
    stmt = user.select().where(user.c.username == username)
    return await conn.fetchrow(stmt)


async def get_users(conn):
    stmt = user.select().order_by(user.c.id)
    return await conn.fetch(stmt)


async def create_user(conn, username, password_hash):
    stmt = user.insert().values(username=username,
                                password_hash=password_hash)
    await asyncio.shield(conn.execute(stmt))


async def get_topics(conn):
    return await conn.fetch(topic.select())


async def get_topic_by_id(conn, topic_id):
    stmt = topic.select().where(topic.c.id == topic_id)
    return await conn.fetchrow(stmt)


async def create_topic(conn, name):
    stmt = topic.insert().values(name=name)
    await asyncio.shield(conn.execute(stmt))


async def update_topic(conn, topic_id, name):
    stmt = topic.update().where(topic.c.id == topic_id).values(name=name)
    await asyncio.shield(conn.execute(stmt))


async def delete_topic(conn, topic_id):
    stmt = topic.delete().where(topic.c.id == topic_id)
    await asyncio.shield(conn.execute(stmt))


async def get_threads_by_topic_id(conn, topic_id):
    stmt = thread.select().where(thread.c.topic == topic_id)
    return await conn.fetch(stmt)


async def create_thread(conn, title, topic_id):
    now = datetime.now()
    stmt = thread.insert().values(
        title=title, topic=topic_id, created_at=now
    ).returning(thread.c.id)
    return await asyncio.shield(conn.fetchrow(stmt))


async def get_messages_by_thread_id(conn, thread_id):
    stmt = message.select().where(message.c.thread == thread_id)
    return await conn.fetch(stmt)


async def create_message(conn, content, thread_id,
                         starter=False, parent=None):
    now = datetime.now()
    stmt = message.insert().values(
        content=content, thread=thread_id,
        starter=starter, parent=parent,
        created_at=now, updated_at=now)
    await asyncio.shield(conn.execute(stmt))
