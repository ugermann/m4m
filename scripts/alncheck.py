#!/usr/bin/env python

import sys,os,gzip

aln = gzip.open(sys.argv[3]).readlines()
src = gzip.open(sys.argv[1]).readlines()[:len(aln)]
trg = gzip.open(sys.argv[2]).readlines()[:len(aln)]

# assert(len(src) == len(trg) and len(trg) == len(aln))
for i in xrange(len(src)):
    print src[i]
    print trg[i]
    print aln[i]
    s = src[i].strip().split()
    t = trg[i].strip().split()
    a = [[int(x) for x in y.split('-')] for y in aln[i].strip().split()]
    A = [[] for x in s]
    for x,y in a:
        A[x].append(y)
        pass
    for k in xrange(len(s)):
        print "%3d %15s"%(k,s[k]),
        for j in A[k]:
            print "%d:%s"%(j,t[j]),
            pass
        print
        pass
    print
    pass

