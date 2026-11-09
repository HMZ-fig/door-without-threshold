# EPRINT-SUBMISSION — 逐字段填写单（照抄即可）

> 依据：2026-11-09 实查 `eprint.iacr.org/submit` 的表单字段名：
> `title, abstract, category, keywords, publcode, iacrpubl, iacryear, origpubl, origdoi, revisiontype, submitpdf, note, license, confirmation`。
> 作者信息取自 `_finals/_meta/authors.json`，未推断。

## 1. Title

```
The Door Without a Threshold: A Lane-Level Case Study of Configuration Authority in Cross-Chain Bridges
```

## 2. Authors（逐个 Add author，顺序即论文顺序）

```
Name         Mingzhao Huang
Affiliation  Shanghai Jiao Tong University   （可写 School of Computer Science）
Email        huangmingzhao@sjtu.edu.cn
ORCID        0009-0009-1620-5506           （可选字段，填这里，不进正文）
```
**——至少一个作者要有邮箱；非匿名，首页必须有姓名与单位（已满足）。**

## 3. Abstract（纯文本，1,940 字符）

```
LayerZero's OApp source-side configuration governs what its endpoint sends, through four doors: the OApp owner, the endpoint delegate, the EIP-1967 admin, and the send-side verifier set. Security reporting usually compresses these into a k-of-n reading, which presumes that a threshold exists to be read. That presumption fails on 122 of the 730 effective lanes of the arbitrum to dstEid 30101 corridor (132 of the 740 catalogued): there the owner is a role system, a proxy whose admin exposes no threshold, or an address with no code, so the owner door exposes no k: for 62 of them the object exists but exposes none, and for 60 there is no object at all. Reading all four doors lane by lane, with the class assignment read at block 522,563,681 and the capability probe pinned at block 522,662,885 and a named denominator on every count, we find 395 lanes (54.1%, D2) on which at least one door can be satisfied by a single key, and the 354 owner-single lanes are held by 225 distinct owners, of which 131 also own weak lanes on base (arbitrum EOA owner set intersected with the base weak-lane owner set), covering 212 of the 354 lanes (59.9%). Counting messages instead of lanes reverses the emphasis: those 395 lanes carry 10.3% of the 694,619 observed packets, while the 107 undetermined lanes carry 40.2%, and the three owner contracts behind 57.0% of the traffic are two 3-of-5 safes and one role system, none of them a single key. The lane table, the owner census, the pinned-block probe and the scripts that regenerate every count are released with the paper, and the procedure is replicated on a second source chain, where 409 of 738 lanes (D2) carry a single-key door. Deployed threshold readings at this granularity do not appear in the incident and audit literature we compare against, whose full texts contain no threshold call and no on-chain address; prevalence, harm, and a third chain remain outside the established result.
```
**——注意：表单会报 “Your abstract contains unprintable characters or invalid UTF-8” 如果从 PDF 复制。**
**——请从本文件的代码块复制，不要从 PDF 复制。**
**——`k-of-n`、`%`、`:` 都已是纯 ASCII，可直接粘贴。**

## 4. Category

```
Applications
```
**——次选 `Cryptographic protocols`（若编辑认为本稿不属于 Applications）。**

## 5. Keywords（逗号分隔，每条 ≤40 字符）

```
cross-chain bridges, configuration authority, threshold, measurement, LayerZero, exposure
```

## 6. Publication information（“Is the submitted paper published elsewhere?”）

```
publcode   → 选 “No”（未在别处发表）
iacrpubl   → 不填
iacryear   → 不填
origpubl   → 不填
origdoi    → 不填
revisiontype → 首次提交选 “New submission”（若页面给该选项）
```

## 7. PDF

```
paper/eprint/main.pdf   （9 页，465 KB，FROZEN 记录的 pdf sha 见 artifact/FROZEN.txt 第 1 行）
```

## 8. Note / Comments（可选）

```
Artifact (data tables, check scripts, frozen manifest) accompanies the paper; every number in the text is
recomputed by code/verify_claims.py from the released data.
```

## 9. License 与确认

```
license      → 选 IACR 默认许可（非独占、不可撤销）
confirmation → 勾选“all authors agree”
```
**——提交后邮件里的密码务必保存：改版、撤稿、写后续历史都用它。**

## 10. 提交前最后三查（可复跑）

```
python3 code/verify_claims.py     → CLAIMS 73 PASS 73 FAIL 0 / COVERAGE 95/95
python3 code/check_scope.py       → SCOPE ok
python3 code/check_boundaries.py  → BOUNDARIES 15/15 PASS
```