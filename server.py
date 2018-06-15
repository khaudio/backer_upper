#!/usr/bin/env python

import signal
from curio import run, spawn, SignalQueue, TaskGroup, Queue, tcp_server, CancelledError, async_thread
from curio.socket import *
from json import dump, loads


delimiter = b'\x80'


async def interpret(line, message, output):
    try:
        payload = loads(line)
        print('Received json')
    except:
        if isinstance(line, bytes):
            if delimiter in line:
                payload = b''.join(message)
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
            await interpret(line, message, output)
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
