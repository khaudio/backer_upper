#!/usr/bin/env python

# TODO:
#     rewrite test file and save under diff name for testing

import signal
from curio import run, spawn, SignalQueue, TaskGroup, Queue, tcp_server, CancelledError, async_thread
from curio.socket import *
from json import dump, loads
from file_checker import check_hash
from os import makedirs, path


preamble, escape = b'\x80' * 3, b'\x81' * 3


async def receive(inc, out):
    message = []
    while True:
        line = await inc.get()
        if escape in line:
            print('Escape sequence found')
            partitioned = line.partition(escape)
            message.append(partitioned[0].lstrip(preamble))
            data = b''.join(message)
            message = [partitioned[2].lstrip(preamble)]
            try:
                meta = loads(data)
            except:
                print('Received payload')
                await out.put(data)
                return
            else:
                print('Received json metadata')
                await out.put(meta)
        elif preamble in line:
            print('Preamble found')
            message = [line.lstrip(preamble)]
        else:
            message.append(line)


def save_payload(meta, payload):
    print('Writing received data')
    name = path.join(meta['client mac'], meta['filename'])
    if not path.exists(meta['client mac']):
        print('Creating client directory')
        makedirs(meta['client mac'])
    with open(name, 'wb') as new:
        new.write(payload)
    print('Data saved')
    return name


async def interpret(inc):
    meta, payload = None, None
    while True:
        data = await inc.get()
        if isinstance(data, dict):
            meta = data
        elif isinstance(data, bytes):
            payload = data
        if meta and payload:
            saved = save_payload(meta, payload)
            if saved:
                if process(meta, saved):
                    print('Transfer completed successfully')
                return


def process(meta, saved):
    print('Verifying received data')
    if check_hash(saved) == meta['sha1']:
        print('Data verified')
        return True
    else:
        print('Data could not be verified')
        return False


async def outgoing(clientStream, output):
    async for msg in output:
        await clientStream.write(msg)


async def incoming(clientStream, output):
    try:
        lines, received = Queue(), Queue()
        async with TaskGroup(wait=any) as workers:
            await workers.spawn(interpret, received)
            await workers.spawn(receive, lines, received)
            async for line in clientStream:
                await lines.put(line)
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
