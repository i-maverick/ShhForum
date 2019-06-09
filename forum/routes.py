from forum.views import (
    index, TopicView, ThreadView, MessageView, LoginView, LogoutView
)


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/topics', TopicView)
    app.router.add_post('/topics', TopicView)
    app.router.add_get('/topics/{id:\d+}', TopicView)
    app.router.add_put('/topics/{id:\d+}', TopicView)
    app.router.add_delete('/topics/{id:\d+}', TopicView)

    app.router.add_get('/topics/{id:\d+}/threads', ThreadView)
    app.router.add_post('/topics/{id:\d+}/threads', ThreadView)

    app.router.add_get('/threads/{id:\d+}/messages', MessageView)
    app.router.add_post('/threads/{id:\d+}/messages', MessageView)

    app.router.add_post('/login', LoginView)
    app.router.add_get('/logout', LogoutView)
