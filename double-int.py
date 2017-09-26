#!/usr/bin/env python
import sys, re
for f in sys.argv[1:]:
	# sed -i -e 's@^\( *\)\(.parent *= *\)\(TYPE_PCI_DEVICE,\)@\1\2TYPE_PCI_DEVICE,\n\1.interfaces = (InterfaceInfo[]) {\n\1    { INTERFACE_LEGACY_PCI_DEVICE },\n\1    { },\n\1},@' $(g grep -l -w TYPE_PCI_DEVICE)
    s = open(f, 'r').read()
    for dec in re.findall(r"TypeInfo *[a-zA-Z_0-9]+ *= *{.*?};", s, flags=re.DOTALL):
        print >>sys.stderr, dec
        # unify double interface decls:
        new = re.sub(r"\n *\.interfaces *= *\(InterfaceInfo\[\]\) *{(.*?)\n *{ *},\n *},*\n(.*)\n( *\.interfaces * = *\(InterfaceInfo\[\]\) *{.*?)(\n *{ *},*\n *},*)\n", r"\n\2\n\3\1\4\n", dec, flags=re.DOTALL)
        s = s.replace(dec, new)
        dec = new

        new = re.sub(r"\n( *\.interfaces *=.*?\n *},*\n)(.*\n)( *};)", r"\n\2\1\3", dec, flags=re.DOTALL)
        s = s.replace(dec, new)
        dec = new

    open(f, 'w').write(s)
