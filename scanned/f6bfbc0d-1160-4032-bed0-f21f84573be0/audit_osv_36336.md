# [H] netfilter: nf_tables: fix inverted genmask check in nft_map_catchall_activate()

## Summary
Severity: High
Advisory: CVE-2026-23111
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2026-23111
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.200, >=5.16.0 <6.1.163, >=6.2.0 <6.6.124, >=6.4.0 <6.12.70, >=6.7.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: fix inverted genmask check in nft_map_catchall_activate()

nft_map_catchall_activate() has an inverted element activity check
compared to its non-catchall counterpart nft_mapelem_activate() and
compared to what is logically required.

nft_map_catchall_activate() is called from the abort path to re-activate
catchall map elements that were deactivated during a failed transaction.
It should skip elements that are already active (they don't need
re-activation) and process elements that are inactive (they need to be
restored). Instead, the current code does the opposite: it skips inactive
elements and processes active ones.

Compare the non-catchall activate callback, which is correct:

  nft_mapelem_activate():
    if (nft_set_elem_active(ext, iter->genmask))
        return 0;   /* skip active, process inactive */

With the buggy catchall version:

  nft_map_catchall_activate():
    if (!nft_set_elem_active(ext, genmask))
        continue;   /* skip inactive, process active */

The consequence is that when a DELSET operation is aborted,
nft_setelem_data_activate() is never called for the catchall element.
For NFT_GOTO verdict elements, this means nft_data_hold() is never
called to restore the chain->use reference count. Each abort cycle
permanently decrements chain->use. Once chain->use reaches zero,
DELCHAIN succeeds and frees the chain while catchall verdict elements
still reference it, resulting in a use-after-free.

This is exploitable for local privilege escalation from an unprivileged
user via user namespaces + nftables on distributions that enable
CONFIG_USER_NS and CONFIG_NF_TABLES.

Fix by removing the negation so the check matches nft_mapelem_activate():
skip active elements, process inactive ones.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://git.kernel.org/stable/c/1444ff890b4653add12f734ffeffc173d42862dd
- https://git.kernel.org/stable/c/42c574c1504aa089a0a142e4c13859327570473d
- https://git.kernel.org/stable/c/8b68a45f9722f2babe9e7bad00aa74638addf081
- https://git.kernel.org/stable/c/8c760ba4e36c750379d13569f23f5a6e185333f5
- https://git.kernel.org/stable/c/b9b6573421de51829f7ec1cce76d85f5f6fbbd7f
- https://git.kernel.org/stable/c/f41c5d151078c5348271ffaf8e7410d96f2d82f8
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-23111.json
- https://access.redhat.com/errata/RHSA-2026:10108
- https://access.redhat.com/errata/RHSA-2026:10996
- https://access.redhat.com/errata/RHSA-2026:18134
- https://access.redhat.com/errata/RHSA-2026:62639
- https://access.redhat.com/errata/RHSA-2026:62641
- https://access.redhat.com/errata/RHSA-2026:6570
- https://access.redhat.com/errata/RHSA-2026:9112
- https://access.redhat.com/security/cve/CVE-2026-23111
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23111.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23111
