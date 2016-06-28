#!/usr/bin/env python3
import sys, os, traceback, contextlib, subprocess, select
import urllib.parse, tempfile, yaml, hashlib, argparse

import logging
logger = logging.getLogger(__name__)
dbg = logger.debug
err = logger.error
warn = logger.warning
info = logger.info

MY_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
DOWNLOAD_DIR = os.path.join(MY_DIR, 'downloads')
IMAGE_FILE = os.path.join(MY_DIR, 'images.yaml')

DEFAULT_TIMEOUT = 10

@contextlib.contextmanager
def changedir(d):
    curdir = os.getcwd()
    try:
        os.chdir(d)
        yield
    finally:
        os.chdir(curdir)

def try_read(f, timeout=None):
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    timeout = int(timeout*1000)

    p = select.poll()
    p.register(f, select.POLLIN)
    r = bytearray()
    dbg("will poll for %d ms", timeout)
    if not p.poll(timeout):
        dbg("timeout (%d) reading %r", timeout, f)
        return None

    dbg("data is available")
    while p.poll(0):
        #TODO: read in larger chunks
        o = f.read(1)
        if not o:
            break
        r.extend(o)
    return r


def qemu_subprocess(d, cmd, **kwargs):
    arch = d['arch']
    env = os.environ.copy()
    env['QEMU'] = 'qemu-system-%s' % (arch)
    dbg('Will run QEMU command: %r', cmd)
    dbg("$QEMU: %r", env['QEMU'])
    return subprocess.Popen(cmd, shell=True, env=env, bufsize=0, **kwargs)

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
        output = bytearray()
        while True:
            #TODO: timeout
            o = try_read(proc.stdout, t.get('timeout'))
            if o is None:
                raise Exception("timeout")
            if not o:
                raise Exception("QEMU process terminated")
            output.extend(o)
            dbg("output is now %d bytes: [%r]", len(output), output[-50:])
            if e in output:
                dbg("Success!")
                break
    finally:
        dbg("terminating QEMU:")
        proc.terminate()
        proc.wait()

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
        raise Exception('Download it first: %s' % (url))

    filehash = sha1file(open(downloaded_file, mode='rb')).hexdigest()
    expectedhash = d['sha1sum'].strip()
    if filehash.lower() != expectedhash.lower():
        raise Exception("sha1 mismatch: %s. expected; %s" % (filehash, expectedhash))

    cmd = d.get('extract-command')
    if not cmd:
        warn('No extract command for %s', url)
        return


    with tempfile.TemporaryDirectory() as td, changedir(td):
        env = os.environ.copy()
        env['FILE'] = downloaded_file
        dbg('will run command: %r', cmd)
        subprocess.Popen(cmd, shell=True, env=env).wait()

        for t in d.get('tests', []):
            m = t['method']
            TEST_METHODS[m](d, t)


def main():

    parser = argparse.ArgumentParser(description='Run test on images based on images.yaml')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help='Debugging messages')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='Verbose mode')
    parser.add_argument('filter', nargs='?', help='filter test names', default=None)
    args = parser.parse_args()

    failures = []
    if args.debug:
        llevel = logging.DEBUG
    elif args.verbose:
        llevel = logging.INFO
    else:
        llevel = logging.WARN
    logging.basicConfig(stream=sys.stderr, level=llevel)

    dlist = yaml.load(open(IMAGE_FILE))
    dbg('dlist: %r', dlist)
    try:
        for d in dlist:
            if args.filter and not args.filter.lower() in d['url'].lower():
                continue

            try:
                info('STARTING: %s', d['name'])
                test_image(d)
                info('SUCCESS: %s', d['name'])
            except Exception as e:
                logging.exception('exception running test')
                info('FAILURE: %s', d['name'])
                failures.append((d,e))  
    finally:
        if failures:
            err('Failure summary:')
            for d,e in failures:
                err('FAILURE: %s: %r', d['name'], e)
        else:
            info('ALL PASSED')

    if failures:
        sys.exit(1)

if __name__ == '__main__':
    main()
