# -*- coding: utf-8 -*-
"""make_readme.py -- 从文件重生成 README 的 inventory 表（FROZEN.txt 不在表内，属自引用）。"""
import csv, hashlib, os

ART = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = []
for d in ('code', 'data'):
    for fn in sorted(os.listdir(os.path.join(ART, d))):
        fp = os.path.join(ART, d, fn)
        if os.path.isfile(fp) and not fn.endswith('.pyc'):
            b = open(fp, 'rb').read()
            files.append((d + '/' + fn, len(b), hashlib.sha256(b).hexdigest()))
table = ['| file | bytes | sha256 |', '|---|---:|---|']
for n, sz, h in files:
    table.append('| `%s` | %s | `%s` |' % (n, format(sz, ','), h))
rd = open(os.path.join(ART, 'README.md'), encoding='utf-8').read()
start = rd.index('| file | bytes | sha256 |')
end = rd.index('## What `reproduce.py` checks')
rd = rd[:start] + '\n'.join(table) + '\n\n' + rd[end:]
open(os.path.join(ART, 'README.md'), 'w', encoding='utf-8').write(rd)
print('README rows', len(table) - 2)