##!/usr/bin/env python3
import subprocess, argparse
from sys import stdout, stderr
from re import findall


class mdbDumper():
    def __init__(self, f, t=False, v=False):
        self.f = f
        self.v = v
        self.t = t
        if not self.t == False:
            self.t = self.t.split(';')
            self.s = self.getSchemaOfTables()
        else:
            self.s = self.getSchema()
            self.t = self.getTablesWithSpaces()

    def getTables(self):
        cmd = subprocess.run(['mdb-tables', self.f],
                             universal_newlines=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if cmd.returncode == 0:
            return cmd.stdout
        if self.v:
            stderr.write("%s\n" % cmd.stderr)

    def getSchema(self):
        cmd = subprocess.run(['mdb-schema', '--drop-table', self.f, 'mysql'],
                             universal_newlines=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if cmd.returncode == 0:
            return cmd.stdout
        if self.v:
            stderr.write("%s\n" % cmd.stderr)

    def getSchemaOfTables(self):
        res = ''
        for table in self.t:
            cmd = subprocess.run(
                ['mdb-schema', '--drop-table', '-T', table, self.f, 'mysql'],
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            if cmd.returncode == 0:
                res += "%s\n" % "\n".join(cmd.stdout.split('\n')[8:])
                continue
            if self.v:
                stderr.write("%s\n" % cmd.stderr)
        return res

    def getTablesWithSpaces(self):
        res = ''
        for i in findall(r'CREATE TABLE.*', self.s):
            i = " ".join(i.split(' ')[2:])
            res += '%s\n' % i.split('`')[1]
        return res

    def getDataOfTables(self):
        res = ''
        for table in self.t:
            cmd = subprocess.run(['mdb-export', '-I mysql', self.f, table],
                                 universal_newlines=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            if cmd.returncode == 0:
                res += '%s\n' % cmd.stdout
                continue
            if self.v:
                stderr.write("%s\n" % cmd.stderr)
        return res


def main():
    p = argparse.ArgumentParser(
        description='Realiza dumps de archivos .mdb y .accdb',
        epilog='Ejemplo: mdbdump db.mdb 1> db.sql')
    p.add_argument('file', help='Fichero .accdb o .mdb')
    p.add_argument('--tables',
                   '-t',
                   default=False,
                   help='Tablas a exportar, separadas por ";"')
    p.add_argument('--verbose',
                   '-v',
                   default=False,
                   help='Muestra salidas de error',
                   action="store_true")
    p.add_argument('--schema',
                   '-s',
                   default=False,
                   action="store_true",
                   help='Vuelca solo el schema')
    p.add_argument('--data',
                   '-d',
                   default=False,
                   action="store_true",
                   help='Vuelca solo los datos')
    args = p.parse_args()
    mdump = mdbDumper(args.file, args.tables, args.verbose)
    if args.data == args.schema:
        stdout.write("%s\n%s" % (mdump.s, mdump.getDataOfTables()))
    elif args.data:
        stdout.write(mdump.getDataOfTables())
    elif args.schema:
        stdout.write(mdump.s)


if __name__ == "__main__":
    main()