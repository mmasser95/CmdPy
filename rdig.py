# !/usr/bin/env python3
import subprocess
import argparse
from sys import stdout, stderr
from re import findall


class dnslkp():
    def __init__(self, d, l=False, v=False, f=False):
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
        stdout.write(self.checkRec())
        if l:
            stdout.write(self.checkLkp())

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
        #return "\n".join(findall(r'^[^;]((\w|\d).*)?$', o))
        return "\n".join(findall(r'[^;]((\w|\d).*)?', o))

    @staticmethod
    def checkDig():
        cmd = subprocess.run(['dig', '-v'])
        if cmd.returncode == 0:
            return True
        return False

    def checkRec(self):
        cmd = subprocess.run(["dig", self.d, "any", "+nocmd", "+nocomments", "+nostat"],
                             universal_newlines=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        print(cmd.returncode)
        if cmd.returncode == 0:
            return self.normalizeOutput(cmd.stdout)
#            return cmd.stdout
        if self.v:
            stderr.write(cmd.stderr)
        return False

    def checkLkp(self):
        res=""
        for subdomain in self.s:
            cmd = subprocess.run(["dig", "%s.%s"%(subdomain,self.d), "any", "+nocmd", "+nocomments", "+nostat"],
                                 universal_newlines=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            if cmd.returncode==0:
                res="%s\n%s"%(res,self.normalizeOutput(cmd.stdout))
            if self.v:
                stderr.write(cmd.stderr)
        return res
