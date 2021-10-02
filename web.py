import json
from aiohttp import web, WSMsgType, WSCloseCode
import aio_pika
import asyncio
import weakref


app = web.Application()
app['websockets'] = weakref.WeakSet()


async def handle(request):
    # name = request.match_info.get('name', "Anonymous")
    text = {'CLIENTES_CONECTADOS': len(app['websockets'])}
    return web.Response(body=json.dumps(text))


async def listen_to_consumer(app):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/",
    )

    queue_name = "hello"

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Declaring queue
        queue = await channel.declare_queue(queue_name)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print(message.body)
                    for ws in app['websockets']:
                        await ws.send_str(message.body.decode())

                    if queue.name in message.body.decode():
                        break


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    request.app['websockets'].add(ws)

    await ws.send_json(data={'test': 'ok'})

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws


async def start_background_tasks(app):
    app['rabbit_listener'] = asyncio.create_task(
        listen_to_consumer(app))


async def cleanup_background_tasks(app):
    app['rabbit_listener'].cancel()
    await app['rabbit_listener']


async def on_shutdown(app):
    for ws in set(app['websockets']):
        await ws.close(code=WSCloseCode.GOING_AWAY,
                       message='Server shutdown')


async def main():
    app.add_routes([web.get('/', handle),
                    web.get('/ws', websocket_handler)])

    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.on_shutdown.append(on_shutdown)

    return app

if __name__ == '__main__':

    web.run_app(main())
