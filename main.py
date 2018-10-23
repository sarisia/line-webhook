import asyncio
from aiohttp import web, ClientSession

from config import Config, Unique 


API_DEST = 'https://api.line.me/v2/bot/message/push'

loop = asyncio.get_event_loop()
routes  = web.RouteTableDef()
session = ClientSession()
config = Config(__file__)
unique = Unique(__file__)

@routes.get('/')
async def get_root(request):
    return web.Response(text='LINE Adapter')

@routes.post('/callback')
async def post_callback(request):
    data = await request.json()
    # TODO: validate

    for event in data['events'] and event['type'] == 'join':
        if event['source']['type'] in ['group', 'room']:
            ret = unique.register(event['source']['groupId'])
            if ret:
                print(f'New hook created: {ret}')

    return web.json_response()

@routes.post('/post/{unique}')
async def post_unique(request):
    dest = unique.get(request.match_info['unique'])
    if not dest:
        return web.json_response(status=400)
    
    data = await request.json()
    content = data.get('content')
    if not content: return web.json_response(status=400)
    
    headers = { 'Authorization': f'Bearer {config.get("token")}'}
    payload = {
        'to': dest,
        'messages': [
            {
               'type': 'text',
               'text': content
            }
        ]
    }

    async with session:
        async with session.post(API_DEST, headers=headers, json=payload) as res:
            if not res.status == 200:
                err = await res.json().get('message')
                print(f'{res.status}: {err}')

    return web.json_response()

if __name__ == '__main__':
    app = web.Application()
    app.add_routes(routes)

    runner = web.AppRunner(app, handle_signals=True)
    loop.run_until_complete(runner.setup())

    site = web.UnixSite(runner, config.get('socket'))

    loop.run_until_complete(site.start())
    print(f'Server started in {site.name}')

    try:
        loop.run_forever()
    except (web.GracefulExit, KeyboardInterrupt):
        pass
    finally:
        loop.run_until_complete(runner.cleanup())

    loop.close()
