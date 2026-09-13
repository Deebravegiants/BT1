# [H] dm-thin: fix metadata refcount underflow

## Summary
Severity: High
Advisory: CVE-2026-46107
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46107
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.259, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm-thin: fix metadata refcount underflow

There's a bug in dm-thin in the function rebalance_children. If the
internal btree node has one entry, the code tries to copy all btree
entries from the node's child to the node itself and then decrement the
child's reference count.

If the child node is shared (it has reference count > 1), we won't free
it, so there would be two pointers to each of the grandchildren nodes.
But the reference counts of the grandchildren is not increased, thus the
reference count doesn't match the number of pointers that point to the
grandchildren. This results in "device mapper: space map common: unable
to decrement block" errors.

Fix this bug by incrementing reference counts on the grandchildren if the
btree node is shared.

## References
- https://git.kernel.org/stable/c/09a65adc7d8bbfce06392cb6d375468e2728ead5
- https://git.kernel.org/stable/c/12161e03d33afce781f68fa11cc6060538862fad
- https://git.kernel.org/stable/c/323d252a4a378834e4fe68298ca61cfc5dd3a460
- https://git.kernel.org/stable/c/5ec0debbcfd43596e32c1239e993de06a704e04c
- https://git.kernel.org/stable/c/85311a585a26640760cd0f3349ab9f2905691044
- https://git.kernel.org/stable/c/b719d12cb94df345e9ad2715fd0abe9afcaeb111
- https://git.kernel.org/stable/c/f06f6aededd792a754cd677c02b3d3016d868c2c
- https://git.kernel.org/stable/c/f49b41c9eb7c6ff00df27cd49cea210abbadd8ad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46107.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46107
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
