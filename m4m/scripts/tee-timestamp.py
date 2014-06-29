#!/usr/bin/env python
# time-stamepd tee: reads lines from stdin, writes them to stdout, and time stamps each line in a separate file

import time,os,sys
from argparse import ArgumentParser

ap = ArgumentParser()
ap.add_argument("-t",help="timestamp file")
ap.add_argument("-o",help="output file",default="/dev/stdout")

args = ap.parse_args(sys.argv[1:])

if os.path.exists(args.o) and args.o != '/dev/stdout':
    print >>sys.stderr,"Will not overwrite existing output file '%s'. "%args.o
    print >>sys.stderr,"Exiting now ..."
    sys.exit(1)
else:
    ofile = open(args.o,'w')
    pass

if os.path.exists(args.t):
    print >>sys.stderr,"Will not overwrite existing timestamp file '%s'. "%args.o
    print >>sys.stderr,"Exiting now ..."
    sys.exit(1)
else:
    tfile = open(args.t,'w')
    pass

zero = time.time()
for line in sys.stdin:
    tlapse     = time.time()-zero
    bytes_read = len(line)
    tfile.wirte("%12.2f %d\n"%(tlapse,bytes_read))
    ofile.write(line)
    pass
