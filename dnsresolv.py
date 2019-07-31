from tld import get_fld
from tld import exceptions as excpt
from dns import resolver
from sys import stdout
import argparse


def getfull(d):
    try:
        d = get_fld(d)
    except excpt.TldBadUrl:
        try:
            d = get_fld(d, fix_protocol=True)
        except:
            d = False
    return d


def getRecords(d, tipos):
    for q in tipos:
        try:
            for i in resolver.query(d, q):
                yield [q, str(i).rstrip('.')]
        except:
            continue


def lkp(d, subd, v=False):
    for i in subd:
        try:
            x = '%s.%s' % (i, d)
            for j in resolver.query(x):
                yield [x, str(j).rstrip('.'), '[OK]']
        except:
            if v:
                yield[x, '', '[FAIL]']
            continue


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description='DNS Lookup del dominio principal y subdominios',
        epilog="Ejemplo: \n 'py main.py -s -f subdomains.txt www.google.com'"
    )
    p.add_argument('dominio', help="El dominio/URL a buscar")
    p.add_argument('-s', '--sublookup',
                   help="Buscar subdominios comunes", action='store_true')
    p.add_argument(
        '-f', '--file', help="Importar subdominios de un archivo, separados por saltos de línea")
    p.add_argument('-v', '--verbose', help="Verbose", action="store_true")
    args = p.parse_args()

    d = getfull(args.dominio)
    tipos = ['A', 'NS', 'MX', 'TXT', 'SOA', 'SRV', 'CERT']
    subd = ['www', 'www2', 'blog', 'cpanel', 'ftp']
    for i in getRecords(d, tipos):
        stdout.write('%s -- %s\n' % (i[0], i[1]))
    if args.sublookup:
        if args.file:
            subd = [x.rstrip() for x in open(args.file).readlines()]
        stdout.write("\n\nLookup\n\n")
        for i in lkp(d, subd, args.verbose):
            stdout.write('%s -- %s -- %s\n' % (i[0], i[2], i[1]))
