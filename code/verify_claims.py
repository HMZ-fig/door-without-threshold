# -*- coding: utf-8 -*-
"""verify_claims.py -- 真执行 claims.tsv 的 command（subprocess），并检查正文数字的覆盖率。

命令列写成 `python3 code/values.py <key>`；在 Windows 上用 sys.executable 执行同一个脚本。
退出：0 全过；1 有 FAIL。末两行：CLAIMS n PASS p FAIL f / COVERAGE p/t
"""
import csv, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.dirname(HERE)
TEX = os.path.join(os.path.dirname(ART), 'eprint', 'main.tex')
ALLOW = {'2025', '2026', '2024', '2023', '2022', '09', '2.5', '30101', '30110', '522563681', '522662885', '26377295', '522673844', '5.4', '8.4', '1.2', '16.79', '588', '209', '27', '1998', '2021', '2022', '0', '01', '3.1', '3.4', '3.5', '4', '8', '9', '11', '14', '16', '42', '48', '3', '1', '2', '6', '7', '10', '12', '13', '15', '19', '31', '87', '255', '256', '107', '549',
         '1967', '1145', '3727648', '3727685', '522385', '413000', '720128', '694619'}


def run(command):
    parts = command.split()
    script = os.path.join(ART, parts[-2])
    key = parts[-1]
    r = subprocess.run([sys.executable, script, key], cwd=ART, capture_output=True, text=True)
    return (r.stdout or '').strip()


def main():
    rows = list(csv.DictReader(open(os.path.join(ART, 'data', 'claims.tsv'), encoding='utf-8'), delimiter='\t'))
    bad = 0
    claimed = set()
    for r in rows:
        got = run(r['command'])
        ok = re.match(r['expected_regex'], got) is not None
        claimed.add(r['number'].replace(',', ''))
        if not ok:
            bad += 1
            print('FAIL %s  %s  expected /%s/  got %s  (%s)' % (r['id'], r['number'], r['expected_regex'], got, r['where']))
    print('CLAIMS %d PASS %d FAIL %d' % (len(rows), len(rows) - bad, bad))
    raw = open(TEX, encoding='utf-8').read().split(chr(10))
    keep = [ln for ln in raw if '\\bibitem' not in ln and 'doi' not in ln and 'arXiv' not in ln and '\\code{' not in ln and not ln.strip().startswith('%')]
    tex = chr(10).join(keep)
    tex = re.sub(r'0x[0-9a-fA-F]+', ' ', tex)
    tex = re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', ' ', tex, flags=re.S)
    tex = re.sub(r'\\begin\{tabular\}\{[^}]*\}', ' ', tex)
    tex = re.sub(r'(L|p)\{[0-9.]+cm\}', ' ', tex)
    tex = re.sub(r'\\arraystretch\}\{[0-9.]+\}', ' ', tex)
    nums = set(m.group(0).rstrip('.').replace(',', '') for m in re.finditer(r'\d[\d,]*\.?\d*', tex))
    missing = sorted(n for n in nums if n not in claimed and n not in ALLOW)
    print('COVERAGE %d/%d' % (len(nums) - len(missing), len(nums)))
    if missing:
        print('UNCLAIMED ' + ' '.join(missing[:60]))
        bad += len(missing)
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())