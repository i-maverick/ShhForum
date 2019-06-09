from forum.security import (
    generate_password_hash,
    check_password_hash
)


async def login_admin(client):
    data = {'username': 'admin', 'password': 'admin'}
    await client.post('/login', json=data)


def test_security():
    user_password = 'qwer'
    hashed = generate_password_hash(user_password)
    assert check_password_hash(user_password, hashed)


async def test_index_view(tables_and_data, client):
    resp = await client.get('/')
    assert resp.status == 200


async def test_topic_view_get(tables_and_data, client):
    resp = await client.get('/topics')
    expected = [
        {'id': 1, 'name': 'Cinema', 'parent': None},
        {'id': 2, 'name': 'Music', 'parent': None},
        {'id': 3, 'name': 'Sport', 'parent': None}
    ]
    assert await resp.json() == expected


async def test_topic_view_get_single(tables_and_data, client):
    resp = await client.get('/topics/1')
    assert await resp.json() == {'id': 1, 'name': 'Cinema', 'parent': None}


async def test_topic_view_get_bad_request(tables_and_data, client):
    resp = await client.get('/topics/Z')
    assert resp.status == 404


async def test_topic_view_get_not_found(tables_and_data, client):
    resp = await client.get('/topics/5')
    assert resp.status == 404


async def test_topic_view_post_anonymous(tables_and_data, client):
    resp = await client.post('/topics', json={'name': 'Food'})
    assert resp.status == 401


async def test_topic_view_post(tables_and_data, client):
    await login_admin(client)
    resp = await client.post('/topics', json={'name': 'Food'})
    assert resp.status == 201
    assert await resp.json() == {'result': 'ok'}


async def test_topic_view_post_bad_json(tables_and_data, client):
    await login_admin(client)
    resp = await client.post('/topics', json=111)
    assert resp.status == 400


async def test_topic_view_post_bad_request(tables_and_data, client):
    await login_admin(client)
    resp = await client.post('/topics')
    assert resp.status == 400


async def test_topic_view_put(tables_and_data, client):
    await login_admin(client)
    resp = await client.put('/topics/3', json={'name': 'Sports'})
    assert resp.status == 200
    assert await resp.json() == {'result': 'ok'}


async def test_topic_view_put_bad_request(tables_and_data, client):
    await login_admin(client)
    resp = await client.put('/topics/4')
    assert resp.status == 400


async def test_topic_view_put_not_found(tables_and_data, client):
    await login_admin(client)
    resp = await client.put('/topics/4', json={'name': 'Food'})
    assert resp.status == 200
    assert await resp.json() == {'result': 'ok'}


async def test_topic_view_delete(tables_and_data, client):
    await login_admin(client)
    resp = await client.delete('/topics/4')
    assert resp.status == 200
    assert await resp.json() == {'result': 'ok'}


async def test_topic_view_delete_not_found(tables_and_data, client):
    await login_admin(client)
    resp = await client.delete('/topics/4')
    assert resp.status == 200
    assert await resp.json() == {'result': 'ok'}


async def test_thread_view_get(tables_and_data, client):
    resp = await client.get('/topics/1/threads')
    expected = [
        {
            'id': 1,
            'title': 'Luc Besson cinematography',
            'topic': 1,
            'created_at': '2001-01-01 00:00:00'
        },
        {
            'id': 2,
            'title': 'Madagascar movie',
            'topic': 1,
            'created_at': '2001-01-01 00:00:00'
        },
    ]
    assert resp.status == 200
    assert await resp.json() == expected


async def test_thread_view_post(tables_and_data, client):
    data = {
        'title': 'Top 100 horrors',
        'content': 'I like scream!'
    }
    resp = await client.post('/topics/1/threads', json=data)
    assert resp.status == 201
    assert await resp.json() == {'result': 'ok'}


async def test_thread_view_post_foreign_key_constraint(tables_and_data, client):
    data = {
        'title': '',
        'content': ''
    }
    resp = await client.post('/topics/10/threads', json=data)
    assert resp.status == 400


async def test_thread_view_post_bad_json(tables_and_data, client):
    resp = await client.post('/topics/1/threads', json=111)
    assert resp.status == 400


async def test_message_view_get(tables_and_data, client):
    resp = await client.get('/threads/1/messages')
    expected = [
        {
            'id': 1,
            'content': 'Le Grand Bleu - the most wonderful movie',
            'thread': 1,
            'parent': None,
            'starter': True,
            'created_at': '2001-03-14 11:15:01',
            'updated_at': '2001-03-14 11:15:01'
        },
        {
            'id': 2,
            'content': 'Yes! But Leon is the most dramatic',
            'thread': 1,
            'parent': 1,
            'starter': False,
            'created_at': '2001-03-14 11:17:12',
            'updated_at': '2001-03-14 11:17:12'
        },
        {
            'id': 3,
            'content': 'Remember the Fifth Element',
            'thread': 1,
            'parent': None,
            'starter': False,
            'created_at': '2001-03-14 11:39:21',
            'updated_at': '2001-03-14 11:39:21'
        },
    ]
    assert resp.status == 200
    assert await resp.json() == expected


async def test_message_view_post(tables_and_data, client):
    data = {
        'content': 'We are the champions, my friend...',
    }
    resp = await client.post('/threads/4/messages', json=data)
    assert resp.status == 201
    assert await resp.json() == {'result': 'ok'}


async def test_message_view_post_foreign_key_constraint(tables_and_data, client):
    data = {
        'content': ''
    }
    resp = await client.post('/threads/10/messages', json=data)
    assert resp.status == 400


async def test_message_view_post_bad_json(tables_and_data, client):
    resp = await client.post('/threads/1/messages', json=111)
    assert resp.status == 400


async def test_login_view(tables_and_data, client):
    invalid_form = {
        'username': 'user',
        'password': '1234'
    }
    valid_form = {
        'username': 'guest',
        'password': 'guest'
    }

    resp = await client.post('/login', json=invalid_form)
    assert resp.status == 200
    assert await resp.json() == {'error': 'Invalid username or password'}

    resp = await client.post('/login', json=valid_form)
    assert resp.status == 200
    assert await resp.json() == {'result': 'ok'}


async def test_logout_view(tables_and_data, client):
    resp = await client.get('/logout')
    assert resp.status == 200
    assert await resp.json() == {'result': 'ok'}
