# [H] netrom: fix double-free in nr_route_frame()

## Summary
Severity: High
Advisory: CVE-2026-23098
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-23098
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.249, >=5.11.0 <5.15.199, >=5.16.0 <6.1.162, >=6.2.0 <6.6.122, >=6.7.0 <6.12.68, >=6.13.0 <6.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netrom: fix double-free in nr_route_frame()

In nr_route_frame(), old_skb is immediately freed without checking if
nr_neigh->ax25 pointer is NULL. Therefore, if nr_neigh->ax25 is NULL,
the caller function will free old_skb again, causing a double-free bug.

Therefore, to prevent this, we need to modify it to check whether
nr_neigh->ax25 is NULL before freeing old_skb.

## References
- https://git.kernel.org/stable/c/25aab6bfc31017a7e52035b99aef5c2b6bde8ffb
- https://git.kernel.org/stable/c/6e0110ea90313b7c0558a0b77038274a6821caf8
- https://git.kernel.org/stable/c/7c48fdf2d1349bb54815b56fb012b9d577707708
- https://git.kernel.org/stable/c/94d1a8bd08af1f4cc345c5c29f5db1ea72b8bb8c
- https://git.kernel.org/stable/c/9f5fa78d9980fe75a69835521627ab7943cb3d67
- https://git.kernel.org/stable/c/ba1096c315283ee3292765f6aea4cca15816c4f7
- https://git.kernel.org/stable/c/bd8955337e3764f912f49b360e176d8aaecf7016
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23098.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23098
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
