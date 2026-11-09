"""predicates.py -- single shared definitions for lane statistics.

Rule: never test literals such as kind == 'eoa' or k == '1'; call these helpers.
"""

ZERO = "0x0000000000000000000000000000000000000000"


def is_zero(addr):
    """True for the zero address AND for a zero integer (code length, threshold, delay).

    The int branch exists because callers pass eth_getCode lengths (int 0 = EOA) as well as
    hex addresses; testing them with a bare `== 0` outside this file is what gate_predicates
    is meant to stop.
    """
    if isinstance(addr, int):          # bool is an int subclass: False -> 0 -> True
        return addr == 0
    return (addr or "").strip().lower() in ("0", "0x0", ZERO)


def k_of(owner_rec):
    """Return int threshold if the owner record exposes one, else None."""
    if not owner_rec:
        return None
    k = owner_rec.get("threshold", owner_rec.get("k"))
    if k is None or k == "":
        return None
    try:
        return int(k)
    except (TypeError, ValueError):
        return None


def is_single_key(owner_rec):
    """Single key: k == 1 (includes 1-of-n Safe), or EOA with threshold 1."""
    if not owner_rec:
        return False
    k = k_of(owner_rec)
    if k is not None:
        return k == 1
    return owner_rec.get("kind") == "eoa"


def vendor_count(lane_rec):
    """Accept both shapes: {'vendors': [...]} and eff-rows {'addrs': 'addr:name|addr:name'}."""
    if lane_rec.get("addrs"):
        parts = [p.split(":") for p in str(lane_rec["addrs"]).split("|") if ":" in p]
        return len({p[1].strip().lower() for p in parts if p[1].strip()})
    names = lane_rec.get("vendors") or lane_rec.get("canonicalNames") or []
    return len({str(x).strip().lower() for x in names if str(x).strip()})

def is_fig1(lane_rec):
    return (
        k_of(lane_rec.get("owner")) == 1
        and lane_rec.get("eff") == 4
        and vendor_count(lane_rec) >= 3
    )

def is_one(v):
    """True if the value is exactly the single-key/single-door marker (1).

    Exists so callers never write `attack == 1` or `k_owner == 1` themselves:
    gate_predicates flags any Eq/NotEq comparison on a name containing k/threshold/kind.
    Non-int or None returns False (an unread door is not a single door).
    """
    return isinstance(v, int) and not isinstance(v, bool) and v == 1


def attack_of(eff, k_owner, k_delegate=None, k_admin=None):
    """min over the doors that exist; None if the owner door is unread.

    Door semantics (same as RESULTS / REPAIR):
      eff always exists; k_owner exists but may be unread (None => undetermined);
      k_delegate / k_admin None means the door does not exist (no constraint).
    """
    doors = [d for d in (eff,) if isinstance(d, int)]
    if isinstance(k_owner, int):
        doors.append(k_owner)
    for d in (k_delegate, k_admin):
        if isinstance(d, int):
            doors.append(d)
    if any(is_one(d) for d in doors):
        return 1
    if not isinstance(k_owner, int):
        return None
    return min(doors) if doors else None

def is_eoa(rec):
    """True when the record says the address is an EOA (no code)."""
    return (rec or {}).get("kind") == "eoa"


def is_contract(rec):
    """True when the record says the address is a contract."""
    return (rec or {}).get("kind") == "contract"


def is_minimal_proxy_clone(nbytes):
    """EIP-1167 minimal proxy byte length (23)."""
    return nbytes == 23
