# [C] dmaengine: idxd: fix possible wrong descriptor completion in llist_abort_desc()

## Summary
Severity: Critical
Advisory: CVE-2026-31436
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31436
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: idxd: fix possible wrong descriptor completion in llist_abort_desc()

At the end of this function, d is the traversal cursor of flist, but the
code completes found instead. This can lead to issues such as NULL pointer
dereferences, double completion, or descriptor leaks.

Fix this by completing d instead of found in the final
list_for_each_entry_safe() loop.

## References
- https://git.kernel.org/stable/c/0e4f43779d550e559be13a5cdb763bad92c4cc99
- https://git.kernel.org/stable/c/82656e8daf8de00935ae91b91bed43f4d6e0d644
- https://git.kernel.org/stable/c/e1c9866173c5f8521f2d0768547a01508cb9ff27
- https://git.kernel.org/stable/c/e21da2ad8844585040fe4b82be1ad2fe99d40074
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31436.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31436
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
