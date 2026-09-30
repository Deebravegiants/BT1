# [H] drm/buddy: Fix alloc_range() error handling code

## Summary
Severity: High
Advisory: CVE-2024-26911
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26911
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/buddy: Fix alloc_range() error handling code

Few users have observed display corruption when they boot
the machine to KDE Plasma or playing games. We have root
caused the problem that whenever alloc_range() couldn't
find the required memory blocks the function was returning
SUCCESS in some of the corner cases.

The right approach would be if the total allocated size
is less than the required size, the function should
return -ENOSPC.

## References
- https://git.kernel.org/stable/c/4b59c3fada06e5e8010ef7700689c71986e667a2
- https://git.kernel.org/stable/c/8746c6c9dfa31d269c65dd52ab42fde0720b7d91
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26911.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26911
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
