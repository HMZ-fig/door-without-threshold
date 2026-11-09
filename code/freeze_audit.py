# -*- coding: utf-8 -*-
"""freeze_audit.py -- 重算 FROZEN.txt 里的每个 sha256，报 mismatch 数。"""
import hashlib, os, sys

ART = 'E:/Projects/crosschain-trust/paper/artifact'
F = os.path.join(ART, 'FROZEN.txt')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    bad = 0
    for ln in open(F, encoding='utf-8'):
        if ln.startswith('#'):
            continue
        parts = ln.split()
        if len(parts) != 2:
            continue
        h, name = parts
        p = 'E:/Projects/crosschain-trust/paper/eprint/main.pdf' if name == 'pdf' else os.path.join(ART, name)
        if not os.path.exists(p):
            print('MISSING', name)
            bad += 1
        elif sha(p) != h:
            print('MISMATCH', name)
            bad += 1
    print('FREEZE-AUDIT %d mismatch' % bad)
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())