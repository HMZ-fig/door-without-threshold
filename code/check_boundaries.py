# -*- coding: utf-8 -*-
"""check_boundaries.py -- Table 4 每行一个真判据。"""
import csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.dirname(HERE)
TEX = os.path.join(os.path.dirname(ART), 'eprint', 'main.tex')
sys.path.insert(0, HERE)
import values


def tex():
    return open(TEX, encoding='utf-8').read().lower()


def main():
    rows = json.load(open(os.path.join(ART, 'data', 'boundaries.json'), encoding='utf-8'))['rows']
    v = values.compute()
    t = tex()
    scope = json.load(open(os.path.join(ART, 'data', 'scope.json'), encoding='utf-8'))
    units = [r['unit'] for r in csv.DictReader(open(os.path.join(ART, 'data', 'lane-doors.csv'), encoding='utf-8-sig'))]
    preds = open(os.path.join(ART, 'code', 'predicates.py'), encoding='utf-8').read()

    def absent(*phrases):
        return not any(p.lower() in t for p in phrases)

    checks = {
        'B01': absent('85\\%', 'roughly', 'recall is near', 'recall of the deployed population is'),
        'B02': all('30101' in u for u in units) and isinstance(scope['dest_read']['block'], int),
        'B03': v['base_lanes'] == 738,
        'B04': v['cross_owners'] == 131,
        'B05': v['und_d2'] == 107,
        'B06': v['cls_T6'] == 10,
        'B07': absent('usd', 'price per', 'market cap'),
        'B08': isinstance(scope['source_read']['class_block'], int) and isinstance(scope['dest_read']['block'], int),
        'B09': v['packets_total'] == 694619,
        'B10': v['unmapped_packets'] == 25509,
        'B11': v['cls_T2'] == 56,
        'B12': absent('signer sets are stable', 'will remain'),
        'B13': 'def attack_of' in preds and 'T6_no_code_on_chain' in open(os.path.join(ART, 'data', 'owner-door-classes.json'), encoding='utf-8').read(),
        'B14': absent('severity', 'weapon', 'exploitability score'),
        'B15': v['cls_T2'] + v['cls_T5b'] + v['cls_T4'] + v['cls_T3c'] + v['cls_T3'] + v['cls_T6'] == 132,
    }
    ok = 0
    for r in rows:
        if checks.get(r['id'], False):
            ok += 1
        else:
            print('OPEN %s  %s  (%s)' % (r['id'], r['boundary'], r['check']))
    print('BOUNDARIES %d/%d PASS' % (ok, len(rows)))
    return 0 if ok == len(rows) else 1


if __name__ == '__main__':
    sys.exit(main())