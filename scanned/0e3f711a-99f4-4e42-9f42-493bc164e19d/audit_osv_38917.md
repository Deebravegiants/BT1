# [H] xfs: don't irele after failing to iget in xfs_attri_recover_work

## Summary
Severity: High
Advisory: CVE-2026-43063
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-43063
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfs: don't irele after failing to iget in xfs_attri_recover_work

xlog_recovery_iget* never set @ip to a valid pointer if they return
an error, so this irele will walk off a dangling pointer.  Fix that.

## References
- https://git.kernel.org/stable/c/40082d08b638485cbaa543dc8087a3d1844d6f08
- https://git.kernel.org/stable/c/70685c291ef82269180758130394ecdc4496b52c
- https://git.kernel.org/stable/c/a1a5df1038f0b3c560d204270373621a4e622808
- https://git.kernel.org/stable/c/b5c5a50c2f513d4a13a6763564a07b470e69cc5a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43063.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43063
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
