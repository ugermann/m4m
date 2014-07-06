#!/usr/bin/env python
# runs a process and monitors its resource use
# written by Ulrich Germann

import sys,os,time,ctypes

zero = time.time()

class Stat:
    # see man page for 'proc' for documentation of process info
    colheaders = ["tstamp", "threads", "state", "wall", 
                  "utime","cutime", "stime","cstime",
                  "VmSize", "RSS", "majflt", "cmajflt", 
                  "read", "write", "load"]
    colheadstr = "# %-13s threads S "%'tstamp' 
    for i in xrange( 3, 8): colheadstr += "%12s "%colheaders[i]
    for i in xrange( 8,10): colheadstr +=  "%6s "%colheaders[i]
    for i in xrange(10,12): colheadstr +=  "%8s "%colheaders[i]
    for i in xrange(12,14): colheadstr += "%12s "%colheaders[i]
    colheadstr += "%5s"%'load'

    def __init__(self,pid):
        self.pid     = pid
        self.status  = {}
        self.io      = {}
        self.tstamp  = time.localtime()
        self.wtime   = 0
        self.utime   = 0
        self.stime   = 0
        self.cutime  = 0
        self.cstime  = 0
        self.minflt  = 0
        self.cminflt = 0
        self.majflt  = 0
        self.cmajflt = 0
        return

    def update(self):
        self.tstamp = time.localtime()
        if not os.path.exists('/proc/%d'%self.pid):
            return False
        self.load = [x.strip() for x in open("/proc/loadavg").readline().strip().split()]
        statusfile = open("/proc/%d/status"%self.pid)
        if not statusfile: return 
        for line in statusfile:
            x = line.strip().split(':')
            if (len(x) < 2): continue
            self.status[x[0].strip()] = x[1].strip().split()
            pass
        if self.status['State'][0] == 'Z': 
            return False
        try:
            for line in open("/proc/%d/io"%self.pid):
                x = line.strip().split(':')
                if (len(x) < 2): continue
                self.io[x[0].strip()] = x[1].strip().split()
                pass
        except:
            self.io['rchar'] = [-1]
            self.io['wchar'] = [-1]
            pass
        F = open("/proc/%d/stat"%self.pid).readline().strip().split()
        self.utime   = int(F[13])/float(os.sysconf(2)) # user time, this process
        self.stime   = int(F[14])/float(os.sysconf(2)) # sy   time, this proc.
        self.cutime  = int(F[15])/float(os.sysconf(2)) # user time, w/ children
        self.cstime  = int(F[16])/float(os.sysconf(2)) # sys  time, w/ children
        self.minflt  = int(F[9])  # minor mem page faults, no reloading required
        self.cminflt = int(F[10]) # same including children
        self.majflt  = int(F[11]) # major mem faults -> page load from disk 
        self.cmajflt = int(F[12]) # same including children
        self.wtime   = (float(open('/proc/uptime').readline().split()[0])
                        - int(F[21])/float(os.sysconf(2)))
        return True
        
    def __str__(self):
        if not len(self.status): self.update()
        if not len(self.status): return ""
        return " ".join([time.strftime("%Y-%m-%d-%H:%M:%S",self.tstamp),
                         "%3d"%int(self.status['Threads'][0]),
                         self.status['State'][0],
                         "%12.2f"%float(self.wtime),
                         "%12.2f"%float(self.utime),
                         "%12.2f"%float(self.cutime),
                         "%12.2f"%float(self.stime),
                         "%12.2f"%float(self.cstime),
                         "%6d"%(int(self.status['VmSize'][0])/1024.),  # MB
                         "%6d"%(int(self.status['VmRSS'][0])/1024.),   # MB  
                         "%8d"%self.majflt,
                         "%8d"%self.cmajflt,
                         "%12.2f"%(int(self.io['rchar'][0])/1048576.), # MB
                         "%12.2f"%(int(self.io['wchar'][0])/1048576.), # MB
                         "%5.2f"%float(self.load[0])
                        ])
    pass

if __name__ == "__main__":
    from subprocess import Popen
    from argparse import ArgumentParser

    ap = ArgumentParser()
    ap.add_argument("-n",type=int,help="delay between polls (in sec)",default=5)
    ap.add_argument("-c",help="command (with args) to be run")
    ap.add_argument("-o",help="name of output file")
    ap.add_argument("pid",nargs='?',type=int,help="id of process to monitor")
    
    try:
        i = sys.argv.index("-c")
        args = ap.parse_args(sys.argv[1:i])
        command = sys.argv[i+1:]
        # print >>sys.stderr,command
        # if len(command) == 1: command = command[0].split()
    except:
        args = ap.parse_args(sys.argv[1:])
        command = []
        pass
    
    if args.o: 
        if os.path.exists(args.o):
            print >>sys.stderr,"Fatal error: procmon logfile '%s'already exists."%args.o
            print >>sys.stderr,"Procmon will not overwrite existing log files."
            print >>sys.stderr,"Exiting now."
            sys.exit(1)
            pass
        logfile = open(args.o,'w')
    else:
        logfile = sys.stdout
        pass

    if len(command):
        pid = os.fork()
        if pid == 0: 
            os.execvp(command[0],command)
        stat = Stat(pid)
    elif args.pid:
        stat = Stat(args.pid)
        pid = None
        pass

    print >>logfile,"# Process log (T: # of threads; S: process state)"
    cmdline = " ".join(open('/proc/%d/cmdline'%stat.pid).readline().split('\0'))
    print >>logfile,'# COMMAND LINE: ',cmdline
    print >>logfile,Stat.colheadstr
    while stat.update():
        logfile.write("%s\n"%str(stat))
        logfile.flush() 
        # print>>sys.stderr, stat
        time.sleep(args.n)
        pass
    
    if pid: 
        checkpid,status = os.wait()
        # print >>sys.stderr,checkpid,status
        sys.exit(status/256)
        pass
    sys.exit(0)
    pass

