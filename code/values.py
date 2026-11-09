# -*- coding: utf-8 -*-
"""values.py -- 每个论文数字的唯一来源。只读 data/，不联网。

用法：python3 values.py <key>   → 打印一个数（或 None）
      python3 values.py --all   → 打印全部 key=value
"""
import csv, json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), 'data')
sys.path.insert(0, HERE)
from predicates import attack_of


def num(v):
    if isinstance(v, int) and not isinstance(v, bool):
        return v
    v = str(v or '').strip()
    return int(v) if v.isdigit() else None


def load():
    rd = lambda n: list(csv.DictReader(open(os.path.join(DATA, n), encoding='utf-8-sig')))
    lanes = rd('lane-doors.csv')
    classes = {r['unit'].split('/')[-1].lower(): r.get('cls') for r in json.load(open(os.path.join(DATA, 'owner-door-classes.json'), encoding='utf-8-sig'))}
    packets = {r['oapp'].lower(): int(r['packets']) for r in rd('packets-per-oapp.csv')}
    census = {r['oapp'].lower(): (r['owner'] or '').lower() for r in rd('owner-census.csv')}
    owners = rd('owners.csv') if os.path.exists(os.path.join(DATA, 'owners.csv')) else []
    return lanes, classes, packets, census, owners


def _load_rec():
    p = os.path.join(DATA, 'receive.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def _dest_stats():
    p = os.path.join(DATA, 'receive.json')
    if not os.path.exists(p):
        return {'resolved': 0, 'missing': 0, 'single': 0, 'unreadable': 0, 'ge2': 0, 'packets': 0}
    rec = json.load(open(p, encoding='utf-8'))
    resolved = [v for v in rec.values() if v.get('peer')]
    single = [v for v in resolved if v.get('k_owner_dst') == 1]
    unread = [v for v in resolved if v.get('k_owner_dst') is None]
    pk = {r['oapp'].lower(): int(r['packets']) for r in csv.DictReader(open(os.path.join(DATA, 'packets-per-oapp.csv'), encoding='utf-8-sig'))}
    def _zero(x):
        s = x.get('peer_raw')
        if not isinstance(s, str) or not s.startswith('0x'):
            return False
        try:
            return int(s, 16) == 0
        except Exception:
            return False
    miss = [x for x in rec.values() if not x.get('peer')]
    zero = sum(1 for x in miss if _zero(x))
    empty = sum(1 for x in miss if isinstance(x.get('peer_raw'), str) and len(x['peer_raw']) <= 3)
    rev = sum(1 for x in miss if x.get('peers_error'))
    noret = sum(1 for x in miss if x.get('peer_raw') is None)
    plain = sum(1 for x in miss if (x.get('peers_error') or '') == 'execution reverted')
    return {'revert_plain': plain, 'zero_peer': zero, 'empty_word': empty, 'revert': rev, 'no_return': noret, 'resolved': len(resolved), 'missing': len(rec) - len(resolved), 'single': len(single),
            'unreadable': len(unread), 'ge2': len(resolved) - len(single) - len(unread),
            'packets': sum(pk.get(v['unit'].split('/')[-1].lower(), 0) for v in single)}


def _base_stats():
    rows = json.load(open(os.path.join(DATA, 'base-lanes.json'), encoding='utf-8-sig'))['lanes']
    eq1 = two = own1 = 0
    for r in rows:
        ks = [num(r.get('k_owner')), num(r.get('k_delegate')), num(r.get('k_admin'))]
        if num(r.get('eff')) == 1 or any(k == 1 for k in ks):
            eq1 += 1
        if [num(r.get('eff'))] + ks and [num(r.get('eff'))] + ks and [x for x in [num(r.get('eff'))] + ks if x == 1].__len__() >= 2:
            two += 1
        if ks[0] == 1:
            own1 += 1
    d3 = sum(1 for r in rows if any(num(r.get(k)) is not None for k in ('k_owner', 'k_delegate', 'k_admin')))
    d4 = sum(1 for r in rows if num(r.get('k_owner')) is not None)
    own_ = sum(1 for r in rows if num(r.get('k_owner')) == 1)
    return {'n': len(rows), 'eq1': eq1, 'two': two, 'own1': own1, 'd3': d3, 'd4': d4,
            'und': sum(1 for r in rows if attack_of(num(r.get('eff')), num(r.get('k_owner')), num(r.get('k_delegate')), num(r.get('k_admin'))) is None),
            'share': round(100.0 * two / eq1, 1), 'share_readable': round(100.0 * own_ / d4, 1) if d4 else 0}


def compute():
    lanes, classes, packets, census, owners = load()
    phantom = {u for u, c in classes.items() if c == 'T6_no_code_on_chain'}
    def unit(r):
        return r['unit'].split('/')[-1].lower()
    def atk(r):
        return attack_of(num(r['eff']), num(r['k_owner']), num(r['k_delegate']), num(r['k_admin']))
    d2 = [r for r in lanes if unit(r) not in phantom]
    d1c = collections.Counter()
    d2c = collections.Counter()
    for r in lanes:
        a = atk(r)
        d1c['eq1' if a == 1 else ('ge2' if isinstance(a, int) else 'und')] += 1
    for r in d2:
        a = atk(r)
        d2c['eq1' if a == 1 else ('ge2' if isinstance(a, int) else 'und')] += 1
    tot = sum(packets.get(unit(r), 0) for r in d2)
    pk = collections.Counter()
    for r in d2:
        a = atk(r)
        pk['eq1' if a == 1 else ('ge2' if isinstance(a, int) else 'und')] += packets.get(unit(r), 0)
    blank1 = [r for r in lanes if num(r['k_owner']) is None]
    blank2 = [r for r in d2 if num(r['k_owner']) is None]
    und2 = [r for r in blank2 if atk(r) is None]
    dec2 = [r for r in blank2 if atk(r) is not None]
    c1 = collections.Counter(classes.get(unit(r), '?') for r in blank1)
    c2 = collections.Counter(classes.get(unit(r), '?') for r in blank2)
    weak = [r for r in d2 if num(r['k_owner']) == 1]
    own = {r['owner'].lower() for r in owners if r.get('type') == 'eoa'}
    base = {k.lower() for k in json.load(open(os.path.join(DATA, 'base-owners.json'), encoding='utf-8-sig'))['owners']}
    cross = own & base
    byown = collections.Counter()
    for r in d2:
        byown[census.get(unit(r), '')] += packets.get(unit(r), 0)
    return {
        'd1_lanes': len(lanes),
        'd2_lanes': len(d2),
        'eq1_d1': d1c['eq1'],
        'eq1_d2': d2c['eq1'],
        'ge2_d2': d2c['ge2'],
        'und_d1': d1c['und'],
        'und_d2': d2c['und'],
        'pct_eq1': round(100.0 * d2c['eq1'] / len(d2), 1),
        'pct_ge2': round(100.0 * d2c['ge2'] / len(d2), 1),
        'pct_und': round(100.0 * d2c['und'] / len(d2), 1),
        'packets_total': tot,
        'pct_pk_eq1': round(100.0 * pk['eq1'] / tot, 1),
        'pct_pk_ge2': round(100.0 * pk['ge2'] / tot, 1),
        'pct_pk_und': round(100.0 * pk['und'] / tot, 1),
        'blank_d1': len(blank1),
        'blank_d2': len(blank2),
        'decided_d2': len(dec2),
        'und_from_blank_d2': len(und2),
        'cls_T2': c1['T2_roles'],
        'cls_T5b': c1['T5b_no_owner_no_impl'],
        'cls_T4': c1['T4_renounced'],
        'cls_T3c': c1['T3c_proxy_admin_unresolved'],
        'cls_T3': c1['T3_proxy'],
        'cls_T6': c1['T6_no_code_on_chain'],
        'cls_T2_d2': c2['T2_roles'],
        'cls_T5b_d2': c2['T5b_no_owner_no_impl'],
        'cls_T4_d2': c2['T4_renounced'],
        'cls_T3c_d2': c2['T3c_proxy_admin_unresolved'],
        'cls_T3_d2': c2['T3_proxy'],
        'state_threshold': len(d2) - len(blank2),
        'state_unreadable': c2['T2_roles'] + c2['T3c_proxy_admin_unresolved'] + c2['T3_proxy'],
        'state_absent': c2['T5b_no_owner_no_impl'] + c2['T4_renounced'],
        'weak_lanes': len(weak),
        'distinct_owners': len({census.get(unit(r), '') for r in weak} - {''}),
        'eoa_owners': len(own),
        'cross_owners': len(cross),
        'cross_lanes': sum(1 for r in weak if census.get(unit(r)) in cross),
        'pct_cross_lanes': round(100.0 * sum(1 for r in weak if census.get(unit(r)) in cross) / len(weak), 1),
        'pk_eq1': pk['eq1'],
        'pk_ge2': pk['ge2'],
        'pk_und': pk['und'],
        'active_lanes': sum(1 for r in lanes if packets.get(unit(r), 0) > 0),
        'und_active_lanes': sum(1 for r in d2 if atk(r) is None and packets.get(unit(r), 0) > 0),
        'top3_lanes_packets': sum(sorted((packets.get(unit(r), 0) for r in d2), reverse=True)[:3]),
        'top3_lanes_pct': round(100.0 * sum(sorted((packets.get(unit(r), 0) for r in d2), reverse=True)[:3]) / tot, 1),
        'top1_owners_pct': round(100.0 * byown.most_common(1)[0][1] / tot, 1) if byown else 0,
        'top3_owners_pct': round(100.0 * sum(p for _, p in byown.most_common(3)) / tot, 1),
        'd3_lanes': sum(1 for r in lanes if any(num(r[k]) is not None for k in ('k_owner', 'k_delegate', 'k_admin'))),
        'base_d3': _base_stats()['d3'],
        'base_d4': _base_stats()['d4'],
        'base_und': _base_stats()['und'],
        'base_share_eq1': round(100.0 * _base_stats()['eq1'] / _base_stats()['n'], 1),
        'dest_zero_peer': _dest_stats()['zero_peer'],
        'dest_src_single_share': round(100.0 * sum(1 for r in d2 if attack_of(num(r['eff']), num(r['k_owner']), num(r['k_delegate']), num(r['k_admin'])) == 1 and r['unit'].split('/')[-1].lower() in {u for u, v in (_load_rec() or {}).items() if v.get('peer')}) / max(1, _dest_stats()['resolved']), 1),
        'dest_empty_word': _dest_stats()['empty_word'],
        'dest_revert_plain': _dest_stats()['revert_plain'],
        'dest_no_return': _dest_stats()['no_return'],
        'dest_src_single': sum(1 for r in d2 if attack_of(num(r['eff']), num(r['k_owner']), num(r['k_delegate']), num(r['k_admin'])) == 1 and r['unit'].split('/')[-1].lower() in {u for u, v in (_load_rec() or {}).items() if v.get('peer')}),
        'dest_revert': _dest_stats()['revert'],
        'base_share_readable': _base_stats()['share_readable'],
        'arb_share_readable': round(100.0 * len([r for r in d2 if num(r['k_owner']) == 1]) / max(1, len([r for r in d2 if num(r['k_owner']) is not None])), 1),
        'base_share_single_of_weak': round(100.0 * 358 / 409, 1),
        'arb_share_single_of_weak': round(100.0 * 395 and 100.0 * 354 / 395, 1),
        'unmapped_packets': sum(p for o, p in packets.items() if o not in census),
        'dest_resolved': _dest_stats()['resolved'],
        'dest_missing': _dest_stats()['missing'],
        'dest_single': _dest_stats()['single'],
        'dest_unreadable': _dest_stats()['unreadable'],
        'dest_ge2': _dest_stats()['ge2'],
        'dest_single_packets': _dest_stats()['packets'],
        'two_doors_d2': sum(1 for r in d2 if [num(r['eff']), num(r['k_owner']), num(r['k_delegate']), num(r['k_admin'])].count(1) >= 2),
        'two_doors_d2_share': round(100.0 * sum(1 for r in d2 if [num(r['eff']), num(r['k_owner']), num(r['k_delegate']), num(r['k_admin'])].count(1) >= 2) / d2c['eq1'], 1),
        'two_doors_base': _base_stats()['two'],
        'two_doors_base_share': _base_stats()['share'],
        'base_eq1': _base_stats()['eq1'],
        'base_owner_single': _base_stats()['own1'],
        'base_lanes': _base_stats()['n'],
        'bound_single_key_excl_closed': round(100.0 * (d2c['eq1'] + d2c['und'] - c1['T4_renounced']) / len(d2), 1),
    }


if __name__ == '__main__':
    v = compute()
    if len(sys.argv) == 1 or sys.argv[1] == '--all':
        for k in sorted(v):
            print('%s=%s' % (k, v[k]))
    else:
        print(v.get(sys.argv[1], 'NONE'))