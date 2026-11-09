# Artifact — The Door Without a Threshold

**Repository.** <https://github.com/HMZ-fig/door-without-threshold>

**Purpose.** Reproduce every number in the paper from released data, without network access.

## Quick start

```
python3 code/reproduce.py          # 28 checks, exit 0 = the paper's numbers hold
```

Requires Python 3.9+ and nothing else (standard library only; `predicates.py` is bundled).

## Inventory (sha256)

| file | bytes | sha256 |
|---|---:|---|
| `code/check_boundaries.py` | 2,280 | `64302371cc1e4fd2736581c85b1bc2a5948ca187e1e6d798fed36a2c4c34a701` |
| `code/check_scope.py` | 1,503 | `a9641e6f3726d1cad82201f79f1a710b6fc8eebdfde077ca89bf52cdbdc4c426` |
| `code/derive_packets.py` | 1,181 | `c49e458a26e6cf11fa5f83a35a7cd9792f552f39a1d2ff6c3f38557ee1b7bec1` |
| `code/freeze.py` | 1,555 | `2b3114c630ed17bbbbf0d96b2d9331c4d6eaa3a52dcccdf07f056c8a23d76141` |
| `code/freeze_audit.py` | 927 | `6cf695fcba7473a2d8764cdefa8ba7c02f961d8975754a07dd98f98caf3bde6c` |
| `code/get_scope_count.py` | 221 | `7ee75f4fec45bccfa937b25f02082b7ca36fa7fc622633a9ce8d065bd1ab67f3` |
| `code/make_readme.py` | 1,007 | `10af356a7061b108ec81927f3e9d8532026692b13e9433195ffc87d5b12c1153` |
| `code/predicates.py` | 3,430 | `58274fd6eb155b61d6b0ada5ece70c9d9fec6d030ef3413b40e5d16185ef4447` |
| `code/reproduce.py` | 5,860 | `6d0af32dd6bceb54f0544cd51f1f7074f7ea68a968bcf915a9ab508602adfe2c` |
| `code/values.py` | 10,970 | `a6de8e2e82784231aab1d1e1d83d29aef46cc69730e2c8cbd149a0c938874247` |
| `code/verify_claims.py` | 2,460 | `46303ef980a56dfd9cbdd00d1f413645a5eaad54c910e80edbcdc87e3221cf50` |
| `data/base-lanes.json` | 182,191 | `fefe0b175012df0d485506b9bc4616a6020006c5bd2a4044cf598bde3f107078` |
| `data/base-owners.json` | 12,608 | `b9d38a6e130ebb2330708b37cc124d3ac1ae352446f182f8dd2df07f4a9d1ccd` |
| `data/boundaries.json` | 2,304 | `47e29bb21621aa81947f50825e0a8af9579572c2d3b062efd16d72aa913b1198` |
| `data/claims.tsv` | 4,585 | `17bc6e92def1a6b0c7e57e2049e6082e4afacea311545989edf772fe82eea846` |
| `data/lane-doors.csv` | 52,466 | `e45f884bcf9a04f4e5e64a221bee262c45e11e23b3248629b3505f608128daa1` |
| `data/owner-census.csv` | 64,443 | `f87da2097af65d741570d26dbfb00e1943ae73ff13e41689c8e9a7704f2ff52e` |
| `data/owner-door-classes.json` | 45,276 | `d9ad8c31cf696dc58e2284b29ab809bdcb6c01ef92fe17721a2a7fe16cbfc18c` |
| `data/owners.csv` | 11,073 | `99c65e6cc7a05f6b82b2a50324583a6e417ed755852df026c70609d9a3147476` |
| `data/packets-per-oapp.csv` | 41,229 | `c9f3b56536693350ae6fa39449fde4aa09d023127142e77bbfa30cbed3e698ad` |
| `data/receive.json` | 188,325 | `4e3512700dabced0f93f7884b4cb1499477e35ef7c1064e24ce94fa926306382` |
| `data/receive_a.json` | 76,444 | `31faf49e2b2aa4ff0365188f0722642329fb28f8f630736aaebaa52bcc19d00b` |
| `data/receive_b.json` | 90,527 | `88649ac7ee5bdda184ae6eef59f4f0b316d876e7694be92f58253670bf2f6178` |
| `data/scope.json` | 1,500 | `d24424b93c16d11de4aa908dd33d6988f534b6aaeb805d8c5d7dd5adc53ef41d` |

## What `reproduce.py` checks (28 assertions)

```
D1 740 lanes ｜ D2 730 lanes
attack==1 395 (D1 and D2) ｜ >=2 228 ｜ undetermined 117 (D1) / 107 (D2)
packets 694,619 ｜ packet shares 10.3% / 49.5% / 40.2%
blank owner door 132 (D1) / 122 (D2) ｜ decided by another door 15 ｜ top-3 owners 57.0% of packets
owner-door states (D2) 608 threshold / 62 unreadable / 60 absent
classes (D1) 56 role, 54 no-owner, 6 renounced, 5 proxy-admin, 1 proxy, 10 no-code —— and the same rows in D2 with 0 no-code
base 738 lanes ｜ 409 attack==1 ｜ 358 owner-single
```

## Provenance

```
lane-doors.csv            one row per (srcChain, dstEid, OApp); four doors + attack; read at the pinned block
owner-door-classes.json   the six classes of the 132 owner doors that admit no k
owner-census.csv          OApp -> owner address
packets-per-oapp.csv      derived from the 720,128 PacketSent events (source sha256 below)
base-lanes.json           the second source chain, same four doors
```

**Raw packet source.** `pk_full.json` (42 MB, 720,128 `PacketSent` events, block window
413,000,009–522,385,536) is not redistributed; `code/derive_packets.py` regenerates
`packets-per-oapp.csv` from it. Its sha256 is
`0dfc6d9448d1353b11f5f9bdfb6a3c0b580f069fc03b29ba9da21644a925b002`.

**Pinned block for the capability probe.** 522,662,885 (0x1f2733e5).

## What is not here

```
raw RPC responses (regenerable; the scripts that issue them are named in the paper's appendix)
the incident corpus of the related-work comparison (third-party, cited by arXiv id)
any price or value data — the paper claims no harm estimate
```

## Licence

Code under `code/` is released under the MIT licence (`LICENSE`). Data under `data/` is released under
CC BY 4.0 (`LICENSE-DATA`).