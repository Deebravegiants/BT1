# [H] hfs: fix potential use after free in hfs_correct_next_unused_CNID()

## Summary
Severity: High
Advisory: CVE-2025-68761
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-68761
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

hfs: fix potential use after free in hfs_correct_next_unused_CNID()

This code calls hfs_bnode_put(node) which drops the refcount and then
dreferences "node" on the next line.  It's only safe to use "node"
when we're holding a reference so flip these two lines around.

## References
- https://git.kernel.org/stable/c/40a1e0142096dd7dd6cb5373841222b528698588
- https://git.kernel.org/stable/c/c105e76bb17cf4b55fe89c6ad4f6a0e3972b5b08
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68761.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68761
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
