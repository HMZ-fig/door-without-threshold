# -*- coding: utf-8 -*-
"""derive_packets.py -- 从原始 PacketSent 导出「每个 OApp 的包数」，供 artifact 使用。

原始 pk_full.json 有 42 MB，不随包发布；这里只导出聚合结果（约 900 行），
并在 README 里记录原始文件的 sha256，使聚合可被追溯到具体输入。
"""
import collections, hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = 'E:/Projects/crosschain-trust'
SRC = os.path.join(ROOT, 'archive/scratch/pk_full.json')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'packets-per-oapp.csv')

b = open(SRC, 'rb').read()
sha = hashlib.sha256(b).hexdigest()
d = json.loads(b.decode('utf-8-sig'))
ev = d['events']
cnt = collections.Counter()
for item in ev:
    cnt[str(item[1]).lower()] += 1
total = sum(cnt.values())
with open(OUT, 'w', encoding='utf-8', newline='') as f:
    f.write('oapp,packets\n')
    for k in sorted(cnt):
        f.write('%s,%d\n' % (k, cnt[k]))
print('source sha256:', sha)
print('events:', len(ev), '| distinct senders:', len(cnt), '| total packets:', total)
print('written:', os.path.normpath(OUT), os.path.getsize(OUT), 'B')