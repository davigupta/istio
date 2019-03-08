#!/usr/bin/env python3
#
# Davi Gupta, Mar 2019
#
# TOKEN=$(curl https://raw.githubusercontent.com/istio/istio/release-1.0/security/tools/jwt/samples/demo.jwt -s)
#

import asyncio
import websockets
import json
import http.client
import logging
import sys
import ssl

headers = {"x-nextensio-codec": "text",
           "x-nextensio-for" : "abc.com",
           "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IkRIRmJwb0lVcXJZOHQyenBBMnFYZkNtcjVWTzVaRXI0UnpIVV8tZW52dlEiLCJ0eXAiOiJKV1QifQ.eyJleHAiOjQ2ODU5ODk3MDAsImZvbyI6ImJhciIsImlhdCI6MTUzMjM4OTcwMCwiaXNzIjoidGVzdGluZ0BzZWN1cmUuaXN0aW8uaW8iLCJzdWIiOiJ0ZXN0aW5nQHNlY3VyZS5pc3Rpby5pbyJ9.CfNnxWP2tcnR9q0vxyxweaF3ovQYHYZl82hAUsn21bwQd9zP7c-LS9qd_vpdLG4Tn1A15NxfCjp5f7QNBUo-KC9PJqYpgGbaXhaGx7bEdFWjcwv3nZzvc7M__ZpaCERdwU7igUmJqYGBYQ51vr2njU9ZimyKkfDe3axcyiBZde7G6dabliUosJvvKOPcKIWPccCgefSj_GNfwIip3-SsFdlR7BtbVUcqR-yv-XOxJ3Uc1MI0tz3uMiiZcyPV7sNCU4KRnemRIMHVOfuvHsU60_GhGbiSFzgPTAa9WTltbnarTbxudb_YEOx12JiwYToeX0DCPb43W1tzIBxgm8NxUg"}

async def aio_readline(greeting):
    line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
    return line

async def consumer(message):
    print(f"> {message}")

async def producer():
    message = await aio_readline("front")
    return message

async def consumer_handler(websocket):
    print("I'm consumer")
    while True:
        message = await websocket.recv()
        await consumer(message)

async def producer_handler(websocket):
    print("I'm producer")
    while True:
        message = await producer()
        await websocket.send(message)

async def hello():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.load_verify_locations('./ingress_ca.pem')
    ssl_context.load_cert_chain(certfile="./ingress_client_cert.pem", keyfile='./ingress_client_key.pem')
    async with websockets.connect(
            'wss://ingress.mesh.nextensio.net', extra_headers=headers, ssl=ssl_context) as websocket:
        await websocket.send("nextensio")
        greeting = await websocket.recv()
        print(f"< {greeting}")
        consumer_task = asyncio.ensure_future(
                            consumer_handler(websocket))
        producer_task = asyncio.ensure_future(
                            producer_handler(websocket))
        done, pending = await asyncio.wait(
                            [consumer_task, producer_task], 
                            return_when=asyncio.FIRST_COMPLETED,)
        for task in pending:
            task.cancel()

if __name__ == '__main__':
    logger = logging.getLogger('websockets.server')
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    asyncio.get_event_loop().run_until_complete(hello())
