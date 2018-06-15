#/usr/bin/env python

from hashlib import md5, sha1, sha256, sha384, sha512
from os import path
from shutil import copyfile, copytree
from time import sleep

"""
Periodically checks and uploads changed files.
"""


targetFiles = (
        'testdata.txt',
    )

tmpDir = '/tmp'
fileHashes = dict()

for f in targetFiles:
    fileHashes[f] = None

def make_temp_copy(currentFile):
    """Duplicate the file to a tmp volume to avoid reading while writing"""
    fileName = currentFile.split('/')[-1]
    tmpFile = path.join(tmpDir, fileName)
    copyfile(fileName, tmpFile)
    return tmpFile


def check_hash(currentFile, blocksize=512000):
    """Hash the contents of the file to check for changes"""
    hasher = sha1()
    with open(currentFile, 'rb') as f:
        block = f.read(blocksize)
        while len(block) > 0:
            hasher.update(block)
            block = f.read(blocksize)
    return hasher.hexdigest()


def main():
    while True:
        changed = []
        for f in targetFiles:
            duplicate = make_temp_copy(f)
            hashed = check_hash(duplicate)
            if hashed != fileHashes[f]:
                changed.append(f)
                fileHashes[f] = hashed
        if changed:
            print('Staged for upload:')
            for stagedFile in changed:
                print(stagedFile)
        sleep(60)


if __name__ == '__main__':
    main()
