# [H] afs: Fix lack of locking around modifications of net->cells_dyn_ino

## Summary
Severity: High
Advisory: CVE-2026-72372
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72372
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.101, >=6.13.0 <6.18.40, >=6.15.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: Fix lack of locking around modifications of net->cells_dyn_ino

Fix the lack of locking around modifications of net->cells_dyn_ino by
taking net->cells_lock exclusively.  This also requires to cell to be
removed from net->cells_dyn_ino in afs_destroy_cell_work() rather than in
afs_cell_destroy() as the latter runs in RCU cleanup context and sleeping
locks cannot be taken there.

## References
- https://git.kernel.org/stable/c/2ffb70a8a01988046bb207b7d0af9358a8337378
- https://git.kernel.org/stable/c/4d8a2fe8847859f4fa4e9a2fa1221c9c1158e66b
- https://git.kernel.org/stable/c/55e841836c6f4646490f7b0347192b7a92d431ba
- https://git.kernel.org/stable/c/e94f92fd56c553a8bf9421c3289e1b85c7c08857
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72372.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72372
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
