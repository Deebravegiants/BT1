# [M] wifi: cw1200: Fix potential NULL dereference

## Summary
Severity: Medium
Advisory: CVE-2024-56536
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56536
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cw1200: Fix potential NULL dereference

A recent refactoring was identified by static analysis to
cause a potential NULL dereference, fix this!

## References
- https://git.kernel.org/stable/c/0ec90ac5f7bd9dd573bd5d964cbdc3beaa93a33e
- https://git.kernel.org/stable/c/2b94751626a6d49bbe42a19cc1503bd391016bd5
- https://git.kernel.org/stable/c/67c914f2d64b28409796a6b9036c131e93f8af6c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56536.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56536
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
