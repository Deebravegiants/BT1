# [H] tipc: reject inverted service ranges from peer bindings

## Summary
Severity: High
Advisory: CVE-2026-74281
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74281
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: reject inverted service ranges from peer bindings

tipc_update_nametbl() inserts a binding advertised by a peer node using
the lower and upper service-range bounds taken directly from the wire,
without checking that lower <= upper. The local bind path validates the
ordering (tipc_uaddr_valid()), but the name-distribution path does not.

A binding with lower > upper is inserted at the far end of the
service-range rbtree (keyed on lower) where no lookup or withdrawal can
ever match it (service_range_foreach_match() requires sr->lower <= end).
The publication, its service_range node and the augmented rbtree entry
are then leaked for the lifetime of the namespace, and there is no
per-peer cap equivalent to TIPC_MAX_PUBL on locally created bindings.

Reject inverted ranges in the network path as well. A peer node can
otherwise leak unbounded binding-table memory by sending PUBLICATION
items with lower > upper.

## References
- https://git.kernel.org/stable/c/2afb648f7b99216c687db1f89739c995e1144153
- https://git.kernel.org/stable/c/581ef56e5c34d475056ce086dc2ba0e872ba6857
- https://git.kernel.org/stable/c/7e401233f9bb74a626e70698d0d62f3a94ac0676
- https://git.kernel.org/stable/c/973bf0ed896b9898668dbadb82ed849d7d573010
- https://git.kernel.org/stable/c/cd1955f81bd8ebeef51b324989ac871ad1947fb6
- https://git.kernel.org/stable/c/f1715d92ee3095d9215b493a8603a81f646fcf61
- https://git.kernel.org/stable/c/f683200b83a0085d4e11abea8c1fdd9fdfb95b0b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74281.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74281
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
