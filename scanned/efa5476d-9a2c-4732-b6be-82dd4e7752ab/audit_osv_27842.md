# [H] ext4: regenerate buddy after block freeing failed if under fc replay

## Summary
Severity: High
Advisory: CVE-2024-26601
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-24
Source: https://osv.dev/vulnerability/CVE-2024-26601
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.211, >=5.11.0 <6.1.78, >=5.16.0 <6.6.17, >=6.2.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: regenerate buddy after block freeing failed if under fc replay

This mostly reverts commit 6bd97bf273bd ("ext4: remove redundant
mb_regenerate_buddy()") and reintroduces mb_regenerate_buddy(). Based on
code in mb_free_blocks(), fast commit replay can end up marking as free
blocks that are already marked as such. This causes corruption of the
buddy bitmap so we need to regenerate it in that case.

## References
- https://git.kernel.org/stable/c/6b0d48647935e4b8c7b75d1eccb9043fcd4ee581
- https://git.kernel.org/stable/c/78327acd4cdc4a1601af718b781eece577b6b7d4
- https://git.kernel.org/stable/c/94ebf71bddbcd4ab1ce43ae32c6cb66396d2d51a
- https://git.kernel.org/stable/c/c1317822e2de80e78f137d3a2d99febab1b80326
- https://git.kernel.org/stable/c/c9b528c35795b711331ed36dc3dbee90d5812d4e
- https://git.kernel.org/stable/c/ea42d6cffb0dd27a417f410b9d0011e9859328cb
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26601.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26601
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
