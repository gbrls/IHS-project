from ast import literal_eval
import asyncio
#from msilib.schema import Component
from random import randint
import websockets
import json
from bindings import *

board_state = None

def build_state():
    s = {}

    s['green_leds'] = [0 for _ in range(0, 17)]
    s['red_leds'] = [0 for _ in range(0, 8)]
    s['push_button'] = [0 for _ in range(0, 4)]
    s['switches'] = [0 for _ in range(0, 17)]
    s['display_left'] = 0xff
    s['display_right'] = 0xff

    return s

async def mock_change_state():
    iter = 0
    while True:
        await asyncio.sleep(0.1)
        #board_state['green_leds'][iter % len(board_state['green_leds'])] = 0
        #iter += 1
        #board_state['green_leds'][iter % len(board_state['green_leds'])] = 1
        for sw in range(0, len(board_state['switches'])):
            board_state['switches'][sw] = read_switch(sw)
        
        for ps in range(0, len(board_state['push_button'])):
            board_state['push_button'][ps] = read_push_btn(ps)
        
        set_red_leds(board_state['red_leds'])
        set_green_leds(board_state['green_leds'])
        write_display(board_state['display_left'], False)

        #board_state['red_leds'][iter % len(board_state['red_leds'])] = 0 
        #board_state['switches'][iter % len(board_state['switches'])] = 0
        #board_state['push_button'][iter % len(board_state['push_button'])] = 0
        #iter += 1
        #board_state['switches'][iter % len(board_state['switches'])] = 1
        #board_state['red_leds'][iter % len(board_state['red_leds'])] = 1
        #board_state['push_button'][iter % len(board_state['push_button'])] = 1



async def send_state(websocket):
    while True:
        await asyncio.sleep(0.5)
        data = json.dumps(board_state, indent=2)
        # print('sending shit')
        await websocket.send(data)

def executeCommand(command):
    if(command["component"] == 'display_left'):
        board_state['display_left'] = command['state']
    else:
        board_state[command['component']][command['index']] = command['state']    
        
    

async def read_commands(websocket):
    async for msg in websocket:
        print(f'received {msg}')
        if(msg != "connected"):
            command = eval(msg)
            executeCommand(command)

async def serve(websocket, path):
    print(f'path: {path}')

    send = asyncio.create_task(send_state(websocket))
    read = asyncio.create_task(read_commands(websocket))

    await send
    await read 

async def main():
#    print(f'btn {read_push_btn(10)}, switch {read_switch(5)}')
 #   c_print_buf([ord(x) for x in "Hello there"])

    init_io()
    mock_change = asyncio.create_task(mock_change_state())

    async with websockets.serve(serve, "localhost", 3001):
        await asyncio.Future()  # run forever
        await mock_change
    end_io()

if __name__ == '__main__':
    board_state = build_state()
    asyncio.run(main())
