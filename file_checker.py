#/usr/bin/env python

# TODO:
    # more hash algs
        # reflected in meta

from hashlib import md5, sha1, sha256, sha384, sha512
from json import dump, dumps, load
from os import path
from shutil import copyfile
from time import sleep

"""
Periodically checks for changed files
"""


# Number of seconds in between each check for changes
numSeconds = 60
assert isinstance(numSeconds, (int, float)), 'Must be integer or float'


def make_tmp_copy(filename, filepath):
    """Duplicate the file to a tmp volume to avoid reading while writing"""
    tmpFile = path.join('/tmp', filename)
    copyfile(filepath, tmpFile)
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


def write_hashes(fileHashes):
    assert isinstance(fileHashes, list), 'Must be list'
    with open('hashes.json', 'w') as hashes:
        dump(fileHashes, hashes, sort_keys=True, indent=4)


def read_hashes():
    if path.exists('hashes.json'):
        with open('hashes.json', 'r') as hashes:
            return load(hashes)
    else:
        return None


def loop(targetFiles):
    fileHashes = read_hashes()
    if not fileHashes:
        fileHashes = [
                {'filename': path.split(f)[-1], 'path': path.abspath(f), 'sha1': None}
                for f in targetFiles
            ]

    # Write to disk every x number of detected changes to lessen wear on local storage
    writeThreshold, detected = 10, 0

    while True:
        changed = []
        for item in fileHashes:
            duplicate = make_tmp_copy(item['filename'], item['path'])
            hashed = check_hash(duplicate)
            if hashed != item['sha1']:
                item['sha1'] = hashed
                changed.append(item)
                # Yield a tuple of the duplicated file for transmission, then metadata
                yield (duplicate, {'filename': item['filename'], 'sha1': item['sha1']})
        if changed:
            detected += 1
            if detected >= writeThreshold or detected is 1:
                print('Writing file hashes to disk')
                write_hashes(fileHashes)
            print('Staged for upload:')
            for stagedFile in changed:
                print(stagedFile)
        sleep(numSeconds)
