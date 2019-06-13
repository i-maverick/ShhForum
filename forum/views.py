from datetime import datetime
import json
import logging

from aiohttp import web
from aiohttp.web import json_response
from aiohttp_security import remember, forget, authorized_userid
import asyncpg

from forum import db
from forum.security import check_password_hash

log = logging.getLogger(__name__)


async def index(request):
    """Dummy response for the root of forum"""
    return web.Response(text='ShhForum')


def json_encoder(data):
    def encoder(o):
        if isinstance(o, datetime):
            return o.__str__()

    return json.dumps(data, default=encoder)


class BaseView(web.View):
    REQUIRED = ()

    def get_object_id(self):
        """Get and validate identifier from url"""
        try:
            object_id = int(self.request.match_info['id'])
        except (TypeError, ValueError):
            raise web.HTTPBadRequest()
        return object_id

    async def get_body_params(self):
        """Validate incoming JSON params"""
        try:
            data = await self.request.json()
        except json.decoder.JSONDecodeError:
            raise web.HTTPBadRequest()

        if not isinstance(data, dict):
            raise web.HTTPBadRequest()

        if not all(item in data for item in self.REQUIRED):
            raise web.HTTPBadRequest()
        return data

    @staticmethod
    async def is_superuser(request, username):
        """Check if current user is admin"""
        async with request.app['db_pool'].acquire() as conn:
            user = await db.get_user_by_name(conn, username)
            return user['superuser']

    @staticmethod
    def ok_response(status=200):
        """Simple Ok response"""
        return json_response({'result': 'ok'}, status=status)


class TopicView(BaseView):
    REQUIRED = ('name',)

    async def get(self):
        """Get all topics or get topic by id
        GET /topics
        """
        topic_id = self.request.match_info.get('id')
        async with self.request.app['db_pool'].acquire() as conn:
            if not topic_id:
                result = await db.get_topics(conn)
                data = list(map(dict, result))
                return json_response(data, dumps=json_encoder)

            topic_id = self.get_object_id()
            data = await db.get_topic_by_id(conn, topic_id)
            if not data:
                raise web.HTTPNotFound()
            return json_response(dict(data))

    async def post(self):
        """Add new topic
        POST /topics
        {
          "name": "string"
        }
        """
        username = await authorized_userid(self.request)
        if not username:
            raise web.HTTPUnauthorized()

        if not await self.is_superuser(self.request, username):
            raise web.HTTPForbidden()

        data = await self.get_body_params()
        async with self.request.app['db_pool'].acquire() as conn:
            await db.create_topic(conn, data['name'])
        return self.ok_response(201)

    async def put(self):
        """Update topic by id
        PUT /topics/{id:int}
        """
        username = await authorized_userid(self.request)
        if not username:
            raise web.HTTPUnauthorized()

        if not await self.is_superuser(self.request, username):
            raise web.HTTPForbidden()

        topic_id = self.get_object_id()
        data = await self.get_body_params()
        async with self.request.app['db_pool'].acquire() as conn:
            await db.update_topic(conn, topic_id, data['name'])
        return self.ok_response()

    async def delete(self):
        """Delete topic by id
        DELETE /topics/{id:int}
        """
        username = await authorized_userid(self.request)
        if not username:
            raise web.HTTPUnauthorized()

        if not await self.is_superuser(self.request, username):
            raise web.HTTPForbidden()

        topic_id = self.get_object_id()
        async with self.request.app['db_pool'].acquire() as conn:
            await db.delete_topic(conn, topic_id)
        return self.ok_response()


class ThreadView(BaseView):
    REQUIRED = ('title', 'content')

    async def get(self):
        """Get all threads by topic id
        GET /topics/{id:int}/threads
        """
        topic_id = self.get_object_id()
        async with self.request.app['db_pool'].acquire() as conn:
            result = await db.get_threads_by_topic_id(conn, topic_id)
            if not result:
                raise web.HTTPNotFound()

            data = list(map(dict, result))
            return json_response(data, dumps=json_encoder)

    # Here should be aiolibs.atomic decorator to make a consistent transaction
    # but unfortunately @asvetlov hasn't implemented it for CBV yet
    async def post(self):
        """Create a new thread in topic
        POST /topics/{id:int}/threads
        {
          "title": "string",
          "content": "string"
        }
        """
        topic_id = self.get_object_id()
        data = await self.get_body_params()
        async with self.request.app['db_pool'].acquire() as conn:
            try:
                thread = await db.create_thread(
                    conn,
                    data['title'],
                    topic_id
                )
                await db.create_message(
                    conn,
                    data['content'],
                    thread['id'],
                    starter=True
                )
            except asyncpg.exceptions.PostgresError as exc:
                log.error(exc)
                return web.HTTPBadRequest()
        return self.ok_response(201)


class MessageView(BaseView):
    REQUIRED = ('content',)

    async def get(self):
        """Get all messages by thread id
        GET /threads/{id:int}/messages
        """
        thread_id = self.get_object_id()
        async with self.request.app['db_pool'].acquire() as conn:
            result = await db.get_messages_by_thread_id(conn, thread_id)
            if not result:
                raise web.HTTPNotFound()

            data = list(map(dict, result))
            return json_response(data, dumps=json_encoder)

    async def post(self):
        """Add new message to thread
        POST /threads/{id:int}/messages
        {
          "content": "string",
          "parent": 0
        }
        """
        thread_id = self.get_object_id()
        data = await self.get_body_params()
        async with self.request.app['db_pool'].acquire() as conn:
            try:
                await db.create_message(
                    conn,
                    data['content'],
                    thread_id,
                    starter=False,
                    parent=data.get('parent')
                )
            except asyncpg.exceptions.PostgresError as exc:
                log.error(exc)
                return web.HTTPBadRequest()
        return self.ok_response(201)


class LoginView(BaseView):
    REQUIRED = ('username', 'password')

    async def post(self):
        """Log in for privileged access
        {
          "username": "string",
          "password": "string"
        }
        """
        username = await authorized_userid(self.request)
        if username:
            return json_response({'error': 'User has already logged in'})

        data = await self.get_body_params()
        username = data['username']
        async with self.request.app['db_pool'].acquire() as conn:
            user = await db.get_user_by_name(conn, username)

            if not user or not check_password_hash(
                    data['password'], user['password_hash']):
                return json_response(
                    {'error': 'Invalid username or password'})

            await remember(self.request, web.Response(), username)
        return self.ok_response()


class LogoutView(BaseView):
    async def get(self):
        """Log out"""
        await forget(self.request, web.Response())
        return self.ok_response()
