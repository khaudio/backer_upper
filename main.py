#!/usr/bin/env python

from json import dumps
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from file_checker import *
from uuid import getnode


targetFiles = (
        'testdata.txt',
    )

serverIP, port = 'localhost', 25000
preamble, delimiter, escape = b'\x80', b'\x81', b'\x82'


def main():
    for changedFile in loop(targetFiles):
        meta = changedFile[1]
        meta['client mac'] = hex(getnode())
        with open(changedFile[0], 'rb') as f:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((serverIP, port))
            s.send(preamble)
            s.send(dumps(meta).encode('utf-8'))
            s.send(delimiter)
            for line in f:
                s.send(line)
            s.send(escape)
            s.shutdown(SHUT_RDWR)
    s.close()


if __name__ == '__main__':
    main()
