#!/usr/bin/env python3
import sys, os, traceback, contextlib, subprocess
import urllib.parse, tempfile, yaml

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
            output += proc.stdout.read(1)
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

def test_image(d):
    dbg('will test %r', d)
    url = d['url']
    path = urllib.parse.urlparse(url).path
    filename = os.path.basename(path)
    downloaded_file = os.path.join(DOWNLOAD_DIR, filename)

    if not os.path.isfile(downloaded_file):
        #TODO: auto-download
        err('Download it first')
        return

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

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

dlist = yaml.load(open(IMAGE_FILE))
dbg('dlist: %r', dlist)
for d in dlist:
    try:
        test_image(d)
    except:
        traceback.print_exc()
