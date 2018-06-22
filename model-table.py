#!/usr/bin/env python
import qemu
import sys

qemubin = sys.argv.pop(1)
refmodel = sys.argv.pop(1)

vm = qemu.QEMUMachine(qemubin)
vm.launch()
cpus = vm.command('query-cpu-definitions')

defs = {}
props = set()
for d in cpus:
    e = vm.command('query-cpu-model-expansion', model={'name':d['name']},
                                                type='full')
    e['propset'] = set(e['model']['props'].items())
    defs[e['model']['name']] = e
    
REMOVE = defs[refmodel]
for n,e in defs.items():
    zeroes = [i for i in e['propset'] if not i[1]]
    print '%s: removing %d zeroes' % (n, len(zeroes))
    e['propset'].difference_update(set(zeroes))
    e['propset'].difference_update(REMOVE['propset'])

for e in defs.values():
    props.update(set(p[0] for p in e['propset']))

props = sorted(props)

props.remove('vendor')
props.remove('model-id')
props.remove('level')
props.remove('xlevel')
props.remove('min-level')
props.remove('min-xlevel')
props.remove('family')
props.remove('model')
props.remove('stepping')

ml = max(map(len, props))
for i in reversed(range(ml)):
    sys.stdout.write('%-12s ' % (''))
    for p in props:
        if len(p) > i:
            sys.stdout.write(p[i])
        else:
            sys.stdout.write(' ')
    sys.stdout.write('\n')

sys.stdout.write('%-12s ' % ('--------'))
for p in props:
    sys.stdout.write('-')
sys.stdout.write('\n')

for d in defs.values():
    sys.stdout.write('%-12s ' % (d['model']['name'][:11]))
    c = 0
    for p in props:
        v = dict(d['propset']).get(p)
        if v:
            sys.stdout.write(str(v)[0])
            c += 1
        else:
            sys.stdout.write(' ')
    sys.stdout.write(' (%d)' % (c))
    sys.stdout.write('\n')
