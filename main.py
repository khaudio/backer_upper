#!/usr/bin/env python

from json import dumps
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from file_checker import *


targetFiles = (
        'testdata.txt',
    )

serverIP, port = 'localhost', 25000
delimiter = b'\x80'

def main():
    for changedFile in loop(targetFiles):
        with open(changedFile, 'rb') as f:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((serverIP, port))
            for line in f:
                s.send(line)
            s.send(delimiter)


if __name__ == '__main__':
    main()
