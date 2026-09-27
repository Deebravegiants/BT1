# [H] netfilter: nf_conncount: fix zone comparison in tuple dedup

## Summary
Severity: High
Advisory: CVE-2026-72247
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72247
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conncount: fix zone comparison in tuple dedup

The "already exists" dedup logic in __nf_conncount_add() decides
whether a connection has already been counted and can be skipped instead
of incrementing the connlimit count.  It compares the conntrack zone of a
list entry with the zone of the connection being added using
nf_ct_zone_id() and nf_ct_zone_equal(), passing conn->zone.dir or
zone->dir as the direction argument.

Those helpers take enum ip_conntrack_dir values: IP_CT_DIR_ORIGINAL is 0
and IP_CT_DIR_REPLY is 1.  However, zone->dir is a u8 bitmask:
NF_CT_ZONE_DIR_ORIG is 1, NF_CT_ZONE_DIR_REPL is 2 and
NF_CT_DEFAULT_ZONE_DIR is 3.  Passing that bitmask as the enum direction
shifts the meaning of every non-zero value.  An ORIG-only zone passes 1
and is tested as REPLY, while REPL-only and default zones pass 2 or 3 and
test bits beyond the valid direction range.  In those cases
nf_ct_zone_id() can fall back to NF_CT_DEFAULT_ZONE_ID instead of using
the real zone id, so different zones can be treated as equal and dedup
collapses to tuple equality alone.

nf_conncount stores and compares the original-direction tuple for a
connection.  If an skb already has an attached conntrack entry,
get_ct_or_tuple_from_skb() explicitly copies
ct->tuplehash[IP_CT_DIR_ORIGINAL].tuple, regardless of the packet's
ctinfo.  Therefore the zone comparison in the tuple dedup path must use
IP_CT_DIR_ORIGINAL as well; the zone direction bitmask describes where a
zone id applies, not which direction this conncount tuple represents.

Fix the two dedup comparisons by passing IP_CT_DIR_ORIGINAL directly.
Do not special-case NF_CT_DEFAULT_ZONE_DIR and do not compare raw zone
ids: using the existing helpers with IP_CT_DIR_ORIGINAL preserves the
direction-aware NF_CT_DEFAULT_ZONE_ID fallback.  A default bidirectional
zone contains the ORIG bit, so it naturally returns the real zone id;
reply-only zones continue to fall back for original-direction tuple
comparisons.

## References
- https://git.kernel.org/stable/c/35a56e2a46b90e6bd4ca816b80e9cb8d20dfc3ce
- https://git.kernel.org/stable/c/3cd9a5792cbea81139c24320986dd0db69e9b5d0
- https://git.kernel.org/stable/c/4f30a89c0ed2418719a1144881c2635b940b543d
- https://git.kernel.org/stable/c/6ff07ac5405bea4d4ead3559fc123f987576424a
- https://git.kernel.org/stable/c/78b5d6dbc860776161f9e9206b06ff8a01f531ab
- https://git.kernel.org/stable/c/7bdc3c0985ecf17b957811fedcc684acdf698acc
- https://git.kernel.org/stable/c/82fc35e0da9a91db9a034f8311f18f77a599ae3f
- https://git.kernel.org/stable/c/f62c41b4910e65da396ec9a8c40c1fe7fe82e449
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72247.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72247
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
