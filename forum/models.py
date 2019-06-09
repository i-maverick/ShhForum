from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, DateTime, Text, Boolean
)


metadata = MetaData()

user = Table(
    'user', metadata,

    Column('id', Integer, primary_key=True),
    Column('username', String(64), nullable=False, unique=True),
    Column('password_hash', String(128), nullable=False),
    Column('superuser', Boolean, nullable=False, default=False)
)

topic = Table(
    'topic', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(64), nullable=False, unique=True),
    Column('parent', Integer, ForeignKey('topic.id'))
)

thread = Table(
    'thread', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(64), nullable=False),
    Column('topic', Integer, ForeignKey('topic.id'), nullable=False),
    Column('created_at', DateTime, nullable=False)
)

message = Table(
    'message', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('content', Text, nullable=False),
    Column('thread', Integer, ForeignKey('thread.id'), nullable=False),
    Column('parent', Integer, ForeignKey('message.id'), nullable=True),
    Column('starter', Boolean, nullable=False, default=False),
    Column('created_at', DateTime, nullable=False),
    Column('updated_at', DateTime, nullable=False)
)
