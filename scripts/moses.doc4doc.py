#!/usr/bin/env python
# A wrapper around moses that feeds multiple documents into moses one by one.
# Intended for context sensitive decoding.
# Author: Ulrich Germann

# usage: moses.doc4doc.py <moses command with arguments>
# NOTE:
# specify the list of documents with -i or --inputput-file 

import os, sys, select, time
from subprocess import Popen, PIPE, check_output

mcmd    = sys.argv[2:]
ifname  = ""

# Pull out arguments related to this wrapper script; 
# store the others in moses_args.
# We also need to keep track of the input file and nbest file arguments.
moses = None
filelist = None
ifile_idx = 0
nbest_idx = 0
moses_args = ["-v", "0"]
show_weights = False
i = 1
while i < len(sys.argv):
    a = sys.argv[i]

    if   a == "--moses":     
        i += 1
        moses = sys.argv[i]
    elif a == "--filelist":
        i += 1
        filelist = sys.argv[i]
    else:
        if a in ["-show-weights", "--show-weights"]:
            show_weights = True
            pass
        moses_args.append(a)
        pass

    if a in ["-i", "-input-file", "--input-file"]:
        ifile_idx = len(moses_args)
    elif a in ["-n-best-list", "--n-best-list"]:
        nbest_idx = len(moses_args)

    i += 1
    pass

if show_weights:
    print check_output([moses]+moses_args)
    sys.exit(0)

if ifile_idx == 0:
    moses_args.append("-i")
    ifile_idx = len(moses_args)
    moses_args.append("PLACEHOLDER")


if nbest_idx:
    nbest_name = moses_args[nbest_idx]
else:
    nbest_name = None

def mk_nbest_tmp(doc, nbest_name):
    p = os.path.dirname(nbest_name)
    b = os.path.basename(nbest_name)
    d = os.path.basename(doc)
    if not p: p = '.'
    return "%s/.%s.%s.%d"%(p,b,d,os.getpid())
 
if nbest_name: 
    nbest = open(nbest_name+'_', 'w')
else: 
    nbest = None
    pass

assert filelist, "No input file list specified!"
assert moses, "No moses executable given"

docdir = os.path.dirname(filelist) 
# docs are expected to be in the same directory as the file list, 
# unless an absolute path is given in the file
startline = 0
for doc in open(filelist):
    # document to translate
    doc = doc.strip()
    if doc[0] == '#': continue 
    if doc[0] != '/': doc = "%s/%s"%(docdir,doc) 

    moses_args[ifile_idx] = doc
    
    # local nbest file, if nbest file is requested
    if nbest: 
        nbest_tmp = mk_nbest_tmp(doc, nbest_name)
        moses_args[nbest_idx] = nbest_tmp
        pass
    
    print >>sys.stderr, " ".join([moses] + moses_args)
    # continue
    ilines = open(doc).readlines()
    # M = Popen([moses] + moses_args, stdout=PIPE, stderr=sys.stderr, bufsize=0)
    sys.stderr.write("%s\n"%doc)
    stime = time.time()
    M = Popen([moses] + moses_args, stdout=PIPE, bufsize=0)
    count_lines_out = 0
    numwords = 0
    for line in M.stdout:
        #sys.stderr.write(ilines[count_lines_out])
        #sys.stderr.write(line)
        #sys.stderr.write("\n")
        numwords += len(line.strip().split())
        sys.stderr.write("%d words after %.2f sec.\n"%(numwords, time.time() - stime))
        sys.stdout.write(line)
        sys.stderr.flush()
        count_lines_out += 1
        pass
    delta = time.time() - stime
    sys.stderr.write("%d lines in %.2f sec. (%.2f sec./line): %s\n"%(len(ilines), delta, delta/len(ilines), doc))
    if count_lines_out != len(ilines):
        print >>sys.stderr, "%d in %d out"%(len(ilines),count_lines_out)
    assert count_lines_out == len(ilines) 

    if nbest:
        for line in open(nbest_tmp):
            sid,rest = line.split(' ', 1);
            nbest.write("%d %s"%(startline + int(sid), rest))
            # sys.stderr.write("NBEST %d %s"%(startline + int(sid), rest))
            pass
        os.remove(nbest_tmp)
        pass
    startline += len(open(doc).readlines())
    pass
if nbest: 
    nbest.close()
    os.rename(nbest_name+'_',nbest_name)
    pass

sys.exit(0)
