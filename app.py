keyData = {
    'BT-A':'d',
    'BT-B':'f',
    'BT-C':'j',
    'BT-D':'k',
    'FX-L':'c',
    'FX-R':'m',
    'Start':'return',
    'VOL-L-L':'e',
    'VOL-L-R':'r',
    'VOL-R-L':'i',
    'VOL-R-R':'o'
}

import asyncio
from sanic import Sanic
from sanic_jinja2 import SanicJinja2
from socketio import AsyncServer
from datetime import datetime
from time import mktime
import pyautogui
pyautogui.FAILSAFE = False

sio = AsyncServer(async_mode='sanic')
app = Sanic(__name__)
sio.attach(app)
jinja = SanicJinja2(app)

def millis_interval(start, end):
    """start and end are datetime instances"""
    diff = end - start
    millis = diff.days * 24 * 60 * 60 * 1000
    millis += diff.seconds * 1000
    millis += diff.microseconds / 1000
    return millis

@app.route('/')
@jinja.template('index.html')
async def index(request):
    return {}

@sio.event
async def down(sid, Data):
    timestampPing = datetime.fromtimestamp(Data.get('timestampPing'))
    timestampPong = datetime.now()

    latency = millis_interval(timestampPing, timestampPong)

    await sio.emit('pong', {'latency':latency}, room=sid)

    print(f'Client {sid} keyDown {keyData.get(Data["key"])}! latency is {latency}ms.')
    pyautogui.keyDown(keyData.get(Data['key']))

@sio.event
async def up(sid, Data):
    timestampPing = datetime.fromtimestamp(Data.get('timestampPing'))
    timestampPong = datetime.now()

    latency = millis_interval(timestampPing, timestampPong)

    await sio.emit('pong', {'latency':latency}, room=sid)

    print(f'Client {sid} keyUp {keyData.get(Data["key"])}! latency is {latency}ms.')
    pyautogui.keyUp(keyData.get(Data['key']))

@sio.event
async def connect(sid, environ):
    print(environ)
    print(f'Client {sid} connected')

@sio.event
async def request_disconnect(sid):
    await sio.disconnect(sid)

@sio.event
async def disconnect(sid):
    print(f'Client {sid} disconnected')

app.static('/static', './static')

if __name__ == '__main__':
    app.run(host='0.0.0.0')