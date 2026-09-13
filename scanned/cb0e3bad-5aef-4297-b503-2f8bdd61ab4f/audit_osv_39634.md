# [H] Revert "net/smc: Introduce TCP ULP support"

## Summary
Severity: High
Advisory: CVE-2026-46330
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46330
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "net/smc: Introduce TCP ULP support"

This reverts commit d7cd421da9da2cc7b4d25b8537f66db5c8331c40.

As reported by Al Viro, the TCP ULP support for SMC is fundamentally
broken. The implementation attempts to convert an active TCP socket
into an SMC socket by modifying the underlying `struct file`, dentry,
and inode in-place, which violates core VFS invariants that assume
these structures are immutable for an open file, creating a risk of
use after free errors and general system instability.

Given the severity of this design flaw and the fact that cleaner
alternatives (e.g., LD_PRELOAD, BPF) exist for legacy application
transparency, the correct course of action is to remove this feature
entirely.

## References
- https://git.kernel.org/stable/c/6c505d95c69e27dbf28fea29dc84d2498d69515c
- https://git.kernel.org/stable/c/df31a6b0a3057e66994ad6ccf5d95b9b9514f033
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46330.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46330
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
