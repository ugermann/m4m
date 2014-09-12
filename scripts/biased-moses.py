#!/usr/bin/env python
import sys,os, argparse,errno
from subprocess import *

class Document:
    def __init__(self,docid):
        self.text  = []
        self.docid = docid
        self.bias  = []
        return
    pass

def load_data(txtfile,mapfile):
    txt = [x.strip() for x in open(txtfile)]
    idm = [x.strip() for x in open(mapfile)]
    docs = []
    for i in xrange(len(idm)):
        if i == 0 or idm[i] != idm[i-1]:
            docs.append(Document(idm[i]))
            pass
        docs[-1].text.append(txt[i])
        pass
    return docs

def load_bias(fname):
    ret = {}
    for line in open(fname):
        x = line.strip().split()
        tstid = x[0]
        trnid = x[1]
        score = float(x[2])
        ret.setdefault(tstid,{})
        ret[tstid][trnid] = score
        pass
    return ret

def split_args(args):
    i = 0
    my_args = []
    mo_args = []
    while i < len(args):
        if args[i] in ["--input","-i","--imap","-I","--corpus","-c","--cmap",
                       "-C","--config","-f","--tmpdir","-T", "--bias","-b",
                       "--moses","-m"]:
            my_args.extend(args[i:i+2])
            i += 2
        else:
            mo_args.append(args[i])
            i += 1
            pass
        pass
    return my_args,mo_args
    
my_args,mo_args = split_args(sys.argv[1:])

ap = argparse.ArgumentParser()
ap.add_argument("--input","-i", help="input text")
ap.add_argument("--imap","-I", help="maps from sentence to docid (input)")
ap.add_argument("--corpus","-c", help="training corpus")
ap.add_argument("--cmap","-C", help="maps from sentenc to docid (training data)")
ap.add_argument("--config","-f", help="moses config file")
ap.add_argument("--tmpdir","-T", help="temp dir")
ap.add_argument("--bias","-b", help="externally computed document-level bias")
ap.add_argument("--moses","-m",help="moses executable")
arg = ap.parse_args(my_args)

# print "MOSES ARGS", mo_args

tstfile  = arg.input
tmapfile = arg.imap
trnfile  = arg.corpus
dmapfile = arg.cmap
moconf   = arg.config
biasfile = arg.bias
odir     = arg.tmpdir
inifile  = arg.config
# print "input:",tstfile,tmapfile
# print "corpus:",trnfile,dmapfile
# print "bias:",biasfile
# print "tmp:",odir

tst  = load_data(tstfile,tmapfile)
trn  = load_data(trnfile,dmapfile)
bias = load_bias(biasfile)

D = {}
for d in trn:
    D[d.docid] = d
    pass
dkeys = D.keys()

ini_lines = [x.strip() for x in open(inifile).readlines()]

for t in tst:
    B = bias[t.docid]
    z = 0.
    for d in trn:
        B.setdefault(d.docid,0.)
        t.bias.extend([B[d.docid]] * len(d.text))
        z += B[d.docid]
        pass
    pass
    for i in xrange(len(t.bias)):
        t.bias[i] /= z
        pass
    mydir = "%s/%s"%(os.path.abspath(odir),os.path.basename(tstfile))
    try:
        os.makedirs(mydir)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(mydir):
            pass
        else: raise
        pass
    txtname = "%s/%s.txt"%(mydir,t.docid)
    txtout = open(txtname,'w')
    print >>txtout, "\n".join(t.text)
    txtout.close()
    biasname = "%s/%s.bias"%(mydir,t.docid)
    bias_out = open(biasname,'w')
    print >>bias_out,"\n".join(["%f"%b for b in t.bias])
    bias_out.close()
    ininame = "%s/%s.ini"%(mydir,t.docid)
    ini_out = open(ininame,'w')
    for line in ini_lines:
        if line.find("Mmsapt") == 0:
            print >>ini_out,line, "bias=%s"%biasname
        else:
            print >>ini_out,line
            pass
        pass
    pass
    ini_out.close()
    cmd = [arg.moses,"-f",ininame,"-i",txtname ] + mo_args
    print " ".join(cmd)
    moproc = Popen(cmd,stdout=PIPE)
    for line in moproc.stdout:
        print line.strip()
        pass
    
        
