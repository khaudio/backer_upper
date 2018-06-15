#/usr/bin/env python

from hashlib import md5, sha1, sha256, sha384, sha512
from json import dump, load
from os import path
from shutil import copyfile
from time import sleep

"""
Periodically checks and uploads changed files.
"""


targetFiles = (
        'testdata.txt',
    )

tmpDir, fieldnames = '/tmp', ('filename', 'checksum')
fileHashes = [{'filename': f, 'checksum': 0} for f in targetFiles]

# Write to disk every x number of detected changes to lessen wear on local storage
writeThreshold = 50


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


def write_hashes():
    with open('hashes.json', 'w') as hashes:
        dump(fileHashes, hashes, sort_keys=True, indent=4)


def read_hashes():
    if path.exists('hashes.json'):
        with open('hashes.json', 'r') as hashes:
            fileHashes = load(hashes)


def main():
    read_hashes()
    detected = 0
    while True:
        changed = []
        for f in fileHashes:
            duplicate = make_temp_copy(f['filename'])
            hashed = check_hash(duplicate)
            if hashed != f['checksum']:
                changed.append(f)
                f['checksum'] = hashed
        if changed:
            detected += 1
            if detected >= writeThreshold or detected is 1:
                print('Writing file hashes to disk')
                write_hashes()
            print('Staged for upload:')
            for stagedFile in changed:
                print(stagedFile)
        sleep(60)


if __name__ == '__main__':
    main()
