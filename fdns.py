#!/usr/bin/env python3
import subprocess
import argparse
from threading import Thread, Lock
from queue import Queue
from sys import stdout, stderr
from re import match
EXFLAG = 0
THR = []
wQueue = Queue()
qLock = Lock()


class Handler(Thread):
    def __init__(self, d, v):
        Thread.__init__(self)
        self.d = d
        self.v = v

    @staticmethod
    def normOut(o, sd):
        o = o.split('\n')
        res = ""
        for i in o:
            if match('.* address .*', i):
                res = i.split('address')[1].strip()
                break
        return "%s %s\n" % (sd, res)

    def run(self):
        while not EXFLAG:
            qLock.acquire()
            if not wQueue.empty():
                subdomain = wQueue.get()
                qLock.release()
                cmd = subprocess.run(["host", "%s.%s" % (subdomain, self.d)],
                                     universal_newlines=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
                if cmd.returncode == 0:
                    stdout.write(self.normOut(cmd.stdout, "%s.%s" %
                                              (subdomain, self.d)))
                if self.v:
                    stderr.write(cmd.stderr)
            else:
                qLock.release()


class dnslkp():
    def __init__(self, d, l=False, v=False, f=False):
        global EXFLAG
        if not self.checkDig():
            stderr.write('dnsutils required! Install it.')
            exit(1)
        self.d = d
        self.v = v
        self.s = ""
        if l and not f:
            self.s = self.getSubdomains(l, self.v)
        elif l and f:
            self.s = self.getSubdomains(f, self.v)
        stdout.write("%s\n" % self.checkRec())
        if l:
            self.dolkp()

    @staticmethod
    def getSubdomains(l, v):
        if l == True:
            return['www', 'www2', 'mail', 'smtp', 'crm', 'ftp', 'cpanel', 'web', 'intranet', 'blog', 'antigua', 'old', 'new', 'nueva', 'dev']
        else:
            try:
                with open(l, 'r') as f:
                    return f.readlines()
            except Exception as e:
                if v:
                    stderr.write(e)
        return False

    @staticmethod
    def normalizeOutput(o):
        return "\n".join([x.rstrip() for x in o.split('\n') if match(r'^[^;].*$', x)])

    @staticmethod
    def checkDig():
        cmd = subprocess.run(['dig', '-v'])
        if cmd.returncode == 0:
            return True
        return False

    def checkRec(self):
        cmd = subprocess.run(["dig", self.d, "any", "+nocmd", "+nocomments", "+nostat", "+noauthority"],
                             universal_newlines=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if cmd.returncode == 0:
            return self.normalizeOutput(cmd.stdout)
        if self.v:
            stderr.write(cmd.stderr)
        return False

    def dolkp(self):
        global EXFLAG
        for i in range(10):
            th = Handler(self.d, self.v)
            th.start()
            THR.append(th)

        qLock.acquire()
        for i in self.s:
            wQueue.put(i)
        qLock.release()
        while not wQueue.empty():
            pass
        EXFLAG = 1
        for t in THR:
            t.join()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Fast DNS Lookup',
                                epilog='Ejemplo: fdns -v -l -f subdomains.txt google.com')
    p.add_argument('domain', help='Top-level domain')

    p.add_argument('--lookup', '-l', default=False,
                   help='Lookup Subdominios', action='store_true')
    p.add_argument('--file', '-f', default=False,
                   help='Ruta del archivo con subdominios')
    p.add_argument('--verbose',
                   '-v',
                   default=False,
                   help='Muestra salidas de error',
                   action="store_true")
    args = p.parse_args()
    d = dnslkp(args.domain, args.lookup, args.verbose, args.file)
