# -*- coding: utf-8 -*-
"""check_scope.py -- 校验 scope.json 的四条不变量。"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import values


def main():
    s = json.load(open(os.path.join(ART, 'data', 'scope.json'), encoding='utf-8'))
    v = values.compute()
    c = s['counts']
    errs = []
    if c['n_peer_resolved'] + c['n_peer_missing'] != v['d2_lanes']:
        errs.append('resolved+missing != 730')
    if c['n_owner_agree'] + c['n_owner_disagree'] + c['n_owner_unreadable'] != c['n_peer_resolved']:
        errs.append('agree+disagree+unreadable != resolved')
    if c['missing_zero_peer'] + c['missing_no_return'] + c['missing_empty_word'] != c['n_peer_missing']:
        errs.append('missing categories do not sum')
    if not isinstance(s['dest_read']['block'], int):
        errs.append('dest block not an integer')
    if c['d1_lanes'] != v['d1_lanes'] or c['d2_lanes'] != v['d2_lanes']:
        errs.append('lane counts mismatch')
    if c['n_peer_resolved'] != v['dest_resolved'] or c['n_peer_missing'] != v['dest_missing']:
        errs.append('peer counts disagree with values.py')
    if s['doors']['dest_owner'] not in ('source', 'dest', 'both', 'none'):
        errs.append('doors enum violated')
    for e in errs:
        print('FAIL', e)
    print('SCOPE %s' % ('ok' if not errs else 'FAIL %d' % len(errs)))
    return 0 if not errs else 1


if __name__ == '__main__':
    sys.exit(main())