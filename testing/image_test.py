#!/usr/bin/env python3
import sys, os, traceback, contextlib, subprocess
import urllib.parse, tempfile, yaml, hashlib

import logging
logger = logging.getLogger(__name__)
dbg = logger.debug
err = logging.error

MY_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
DOWNLOAD_DIR = os.path.join(MY_DIR, 'downloads')
IMAGE_FILE = os.path.join(MY_DIR, 'images.yaml')

@contextlib.contextmanager
def changedir(d):
    curdir = os.getcwd()
    try:
        os.chdir(d)
        yield
    finally:
        os.chdir(curdir)

def qemu_subprocess(d, cmd, **kwargs):
    arch = d['arch']
    env = os.environ.copy()
    env['QEMU'] = 'qemu-system-%s' % (arch)
    dbg('Will run QEMU command: %r', cmd)
    return subprocess.Popen(cmd, shell=True, env=env, **kwargs)

def just_run(d, t):
    testcmd = t.get('command')
    assert testcmd
    proc = qemu_subprocess(d, testcmd).wait()

def stdoutwait(d, t):
    testcmd = t.get('command')
    e = bytes(t.get('expect'), 'utf-8')
    assert testcmd
    proc = qemu_subprocess(d, testcmd, stdout=subprocess.PIPE)
    try:
        output = bytes()
        while True:
            #TODO: timeout
            o = proc.stdout.read(1)
            if not o:
                raise Exception("QEMU process terminated")
            output += o
            dbg("output is now %d bytes [%s]", len(output), output[-20:])
            if e in output:
                dbg("Success!")
                break
    finally:
        dbg("terminating QEMU:")
        proc.terminate()

TEST_METHODS = {
    'just_run': just_run,
    'stdoutwait': stdoutwait,
}

def sha1file(f):
    h = hashlib.new('sha1')
    while True:
        b = f.read(4096)
        if not b:
            break
        h.update(b)
    return h

def test_image(d):
    dbg('will test %r', d)
    url = d['url']
    path = urllib.parse.urlparse(url).path
    filename = os.path.basename(path)
    downloaded_file = os.path.join(DOWNLOAD_DIR, filename)

    dbg('downloaded file: %r', downloaded_file)

    if not os.path.isfile(downloaded_file):
        #TODO: auto-download
        err('Download it first')
        return

    filehash = sha1file(open(downloaded_file, mode='rb')).hexdigest()
    expectedhash = d['sha1sum'].strip()
    if filehash.lower() != expectedhash.lower():
        raise Exception("sha1 mismatch: %s. expected; %s" % (filehash, expectedhash))

    cmd = d.get('extract-command')
    if not cmd:
        err('No extract command')
        return


    with tempfile.TemporaryDirectory() as td, changedir(td):
        env = os.environ.copy()
        env['FILE'] = downloaded_file
        dbg('will run command: %r', cmd)
        subprocess.Popen(cmd, shell=True, env=env).wait()

        for t in d.get('tests', ['just_run']):
            m = t['method']
            TEST_METHODS[m](d, t)


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    name = None
    if len(sys.argv) >= 2:
        name = sys.argv[1]

    dlist = yaml.load(open(IMAGE_FILE))
    dbg('dlist: %r', dlist)
    for d in dlist:
        if name is not None and not name.lower() in d['url'].lower():
            continue
        try:
            test_image(d)
        except:
            traceback.print_exc()

if __name__ == '__main__':
    main()
