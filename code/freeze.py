# -*- coding: utf-8 -*-
"""freeze.py -- 生成 FROZEN.txt：pdf + data/* + code/* 的 sha256，并记录上一版以便 diff。"""
import hashlib, json, os, sys

ART = 'E:/Projects/crosschain-trust/paper/artifact'
PDF = 'E:/Projects/crosschain-trust/paper/eprint/main.pdf'
OUT = os.path.join(ART, 'FROZEN.txt')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    rows = [('pdf', PDF), ('README.md', os.path.join(ART, 'README.md'))]
    for d in ('data', 'code'):
        for f in sorted(os.listdir(os.path.join(ART, d))):
            p = os.path.join(ART, d, f)
            if os.path.isfile(p) and not f.endswith('.pyc'):
                rows.append((d + '/' + f, p))
    lines = ['# FROZEN ' + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    for name, p in rows:
        lines.append('%s  %s' % (sha(p), name))
    txt = chr(10).join(lines) + chr(10)
    old = {}
    if os.path.exists(OUT):
        for ln in open(OUT, encoding='utf-8'):
            parts = ln.split()
            if len(parts) == 2 and not ln.startswith('#'):
                old[parts[1]] = parts[0]
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(txt)
    changed = [(n, old.get(n), s) for n, s in [(r[0], sha(r[1])) for r in rows] if old.get(n) not in (None, s)]
    print('FROZEN written:', OUT, '| files:', len(rows), '| changed vs previous:', len(changed))
    for n, o, s in changed:
        print('  CHANGED %s  %s -> %s' % (n, (o or '')[:16], s[:16]))


if __name__ == '__main__':
    main()