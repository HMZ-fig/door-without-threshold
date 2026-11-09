# -*- coding: utf-8 -*-
"""reproduce.py -- 从随包数据重算论文里的每一个数，并断言。

用法：python reproduce.py [--artifact DIR]
退出：0 全部一致；1 有不一致；2 数据缺失

它只读 data/ 下的三个文件 + base-lanes.json + base-owners.json，不联网。
"""
import argparse, collections, csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from predicates import attack_of


def num(v):
    if isinstance(v, int) and not isinstance(v, bool):
        return v
    v = str(v or '').strip()
    return int(v) if v.isdigit() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--artifact', default=os.path.dirname(HERE))
    a = ap.parse_args()
    data = os.path.join(a.artifact, 'data')
    need = ['lane-doors.csv', 'owner-door-classes.json', 'owner-census.csv', 'packets-per-oapp.csv',
            'base-lanes.json', 'base-owners.json']
    for n in need:
        if not os.path.exists(os.path.join(data, n)):
            print('MISSING', n); return 2

    lanes = list(csv.DictReader(open(os.path.join(data, 'lane-doors.csv'), encoding='utf-8-sig')))
    classes = {r['unit'].split('/')[-1].lower(): r.get('cls') for r in json.load(open(os.path.join(data, 'owner-door-classes.json'), encoding='utf-8-sig'))}
    packets = {r['oapp'].lower(): int(r['packets']) for r in csv.DictReader(open(os.path.join(data, 'packets-per-oapp.csv'), encoding='utf-8-sig'))}
    census = {r['oapp'].lower(): (r['owner'] or '').lower() for r in csv.DictReader(open(os.path.join(data, 'owner-census.csv'), encoding='utf-8-sig'))}
    phantom = {u for u, c in classes.items() if c == 'T6_no_code_on_chain'}

    def atk(r):
        g = r.get if hasattr(r, 'get') else (lambda k, d=None: r[k])
        return attack_of(num(g('eff')), num(g('k_owner')), num(g('k_delegate')), num(g('k_admin')))

    d1 = collections.Counter(); d2 = collections.Counter()
    for r in lanes:
        k = 'eq1' if atk(r) == 1 else ('ge2' if isinstance(atk(r), int) else 'und')
        d1[k] += 1
        if r['unit'].split('/')[-1].lower() not in phantom:
            d2[k] += 1

    d2rows = [r for r in lanes if r['unit'].split('/')[-1].lower() not in phantom]
    pk = collections.Counter()
    for r in d2rows:
        o = r['unit'].split('/')[-1].lower()
        pk['eq1' if atk(r) == 1 else ('ge2' if isinstance(atk(r), int) else 'und')] += packets.get(o, 0)
    tp = sum(pk.values())

    d1blank = [r for r in lanes if num(r['k_owner']) is None]
    d2blank = [r for r in d2rows if num(r['k_owner']) is None]
    c1 = collections.Counter(classes.get(r['unit'].split('/')[-1].lower(), '?') for r in d1blank)
    c2 = collections.Counter(classes.get(r['unit'].split('/')[-1].lower(), '?') for r in d2blank)
    und = [r for r in d2blank if atk(r) is None]
    dec = [r for r in d2blank if atk(r) is not None]
    st_thr = len(d2rows) - len(d2blank)
    st_unr = c2['T2_roles'] + c2['T3c_proxy_admin_unresolved'] + c2['T3_proxy']
    st_abs = c2['T5b_no_owner_no_impl'] + c2['T4_renounced']
    top3 = 0
    byown = collections.Counter()
    for r in d2rows:
        o = r['unit'].split('/')[-1].lower()
        byown[census.get(o, '')] += packets.get(o, 0)
    top3 = sum(p for _, p in byown.most_common(3))

    base = json.load(open(os.path.join(data, 'base-lanes.json'), encoding='utf-8-sig'))
    brows = base['lanes']
    b1 = sum(1 for r in brows if atk(r) == 1)
    bown = sum(1 for r in brows if r.get('k_owner') is not None and num(r.get('k_owner')) == 1)

    csv_vs_pred = sum(1 for r in lanes
                     if (r['attack'].strip() or None) != (None if atk(r) is None else str(atk(r))))
    unmapped = sum(p for o, p in packets.items() if o not in census)
    checks = [
        ('D1 lanes', 740, len(lanes)),
        ('D2 lanes', 730, len(d2rows)),
        ('D1 attack==1', 395, d1['eq1']),
        ('D2 attack==1', 395, d2['eq1']),
        ('D2 attack>=2', 228, d2['ge2']),
        ('D2 undetermined', 107, d2['und']),
        ('packets total', 694619, tp),
        ('traffic eq1 %', 10.3, round(100.0 * pk['eq1'] / tp, 1)),
        ('traffic ge2 %', 49.5, round(100.0 * pk['ge2'] / tp, 1)),
        ('traffic und %', 40.2, round(100.0 * pk['und'] / tp, 1)),
        ('D1 blank-owner', 132, len(d1blank)),
        ('D2 blank-owner', 122, len(d2blank)),
        ('D2 decided by other door', 15, len(dec)),
        ('D2 undetermined', 107, len(und)),
        ('T2 roles (D1/D2)', (56, 56), (c1['T2_roles'], c2['T2_roles'])),
        ('T5b no owner (D1/D2)', (54, 54), (c1['T5b_no_owner_no_impl'], c2['T5b_no_owner_no_impl'])),
        ('T4 renounced (D1/D2)', (6, 6), (c1['T4_renounced'], c2['T4_renounced'])),
        ('T3c/T3 (D1/D2)', ((5, 1), (5, 1)), ((c1['T3c_proxy_admin_unresolved'], c1['T3_proxy']), (c2['T3c_proxy_admin_unresolved'], c2['T3_proxy']))),
        ('T6 phantom (D1/D2)', (10, 0), (c1['T6_no_code_on_chain'], c2['T6_no_code_on_chain'])),
        ('state threshold', 608, st_thr),
        ('state unreadable', 62, st_unr),
        ('state absent', 60, st_abs),
        ('top-3 owner share %', 57.0, round(100.0 * top3 / tp, 1)),
        ('base lanes', 738, len(brows)),
        ('base attack==1', 409, b1),
        ('base owner-single', 358, bown),
        ('csv attack == predicate', 0, csv_vs_pred),
        ('unmapped senders %', 3.5, round(100.0 * unmapped / 720128, 1)),
    ]
    bad = 0
    print('%-22s %10s %10s  %s' % ('quantity', 'expected', 'recomputed', ''))
    for name, exp, got in checks:
        ok = (exp == got)
        print('%-22s %10s %10s  %s' % (name, exp, got, 'OK' if ok else 'MISMATCH'))
        if not ok:
            bad += 1
    print()
    print('D1 classes:', dict(c1), '| D2 classes:', dict(c2))
    print('mismatches:', bad)
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())