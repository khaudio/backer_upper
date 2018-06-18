#!/usr/bin/env python

from json import dumps
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from file_checker import *
from uuid import getnode


targetFiles = (
        'testdata.txt',
    )

serverIP, port = 'localhost', 25000
preamble, delimiter, escape = b'\x80' * 3, b'\x81' * 3, b'\x82' * 3
s = socket(AF_INET, SOCK_STREAM)


def transmit(message, file=False):
    s.send(preamble)
    if file:
        with open(message, 'rb') as f:
            for line in f:
                s.send(line)
    else:
        s.send(message)
    s.send(escape)


def main():
    for changedFile in loop(targetFiles):
        meta = changedFile[1]
        meta['client mac'] = hex(getnode())
        s.connect((serverIP, port))
        transmit(dumps(meta).encode('utf-8'))
        transmit(changedFile[0], file=True)
        s.shutdown(SHUT_RDWR)
    s.close()


if __name__ == '__main__':
    main()
