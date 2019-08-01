#!/usr/bin/env python3
import subprocess
import argparse
from sys import stdout, stderr, stdin
from threading import Thread
from re import match
from glob import glob
from shutil import move
from os import path


class Migrate():
    def __init__(self, w):
        self.w = w
        self.dr = []
        self.sn = []
        self.t=self.checkDocumentRoot()
        if self.t == False:
            exit(1)
        else:
            self.runCompress(self.dr[0])
            self.runMysqlDump(self.t)

    def searchPath(self):
        aconfig = glob(path.join('etc', 'apache2',
                                 'sites-enabled', "*%s*.conf" % self.w))[0]
        with open(aconfig,'r') as f:
            lines = f.readlines()
            self.dr = [i for i in lines if match(r'^[^#].*DocumentRoot.*', i)]
            self.sn = [j for j in lines if match(
                r'^[^#].*[ServerName|ServerAlias].*', j)]

    def searchDb(self):
        pass

    def checkDocumentRoot(self):
        if not path.exists(self.dr[0]):
            return False
        elif not len(glob(path.join(self.dr[0],'configuration.php'))):
            return 'joomla'
        elif not len(glob(path.join(self.dr[0],'*wp-config.php'))):
            return 'wp'
        else:
            return 'prompt'

    @staticmethod
    def runCompress(route):
        pass

    @staticmethod
    def runMysqlDump(db):
        pass


if __name__ == "__main__":
    p = argparse.ArgumentParser(description='', epilog='')
    p.add_argument('web', help='The web to migrate')
    args = p.parse_args()
    m = Migrate(args.web)
