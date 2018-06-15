#!/usr/bin/env python

import signal
from curio import run, spawn, SignalQueue, TaskGroup, Queue, tcp_server, CancelledError, async_thread
from curio.socket import *
from json import dump, loads


preamble, delimiter, escape = b'\x80', b'\x81', b'\x82'


async def interpret(line, message, output):
    if isinstance(line, bytes):
        if preamble in line:
            message, payload = [], b''
        elif delimiter in line:
            try:
                meta = loads(b''.join(message))
                yield meta
                print('Received json metadata')
            except:
                print('Unable to parse json metadata')
        elif escape in line:
            payload = b''.join(message)
            yield payload
            message = []
        else:
            message.append(line)
    else:
        pass


async def outgoing(clientStream, output):
    async for msg in output:
        await clientStream.write(msg)


async def incoming(clientStream, output):
    try:
        message = []
        async for line in clientStream:
            async for i in interpret(line, message, output):
                print(i)
    except CancelledError:
        await clientStream.write(b'Server shutting down\n')
        raise


async def client_handler(client, addr):
    print(f'{addr[0]} connected')
    async with client:
        clientStream, output = client.as_stream(), Queue()
        async with TaskGroup(wait=any) as workers:
            await workers.spawn(outgoing, clientStream, output)
            await workers.spawn(incoming, clientStream, output)
    print(f'{addr[0]} disconnected')


async def main(host, port):
    async with SignalQueue(signal.SIGHUP) as restart:
        while True:
            print('Starting the server')
            server = await spawn(tcp_server, host, port, client_handler)
            await restart.get()
            print('Server shutting down')
            await server.cancel()


if __name__ == '__main__':
    run(main('', 25000))
