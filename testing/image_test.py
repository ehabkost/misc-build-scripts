#!/usr/bin/env python3
import sys
import yaml

d = yaml.load(open(sys.argv[1]))
print(repr(d))
