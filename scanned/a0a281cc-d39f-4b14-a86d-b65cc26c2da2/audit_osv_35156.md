# [H] drm/panthor: Prevent potential UAF in group creation

## Summary
Severity: High
Advisory: CVE-2025-68735
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68735
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: Prevent potential UAF in group creation

This commit prevents the possibility of a use after free issue in the
GROUP_CREATE ioctl function, which arose as pointer to the group is
accessed in that ioctl function after storing it in the Xarray.
A malicious userspace can second guess the handle of a group and try
to call GROUP_DESTROY ioctl from another thread around the same time
as GROUP_CREATE ioctl.

To prevent the use after free exploit, this commit uses a mark on an
entry of group pool Xarray which is added just before returning from
the GROUP_CREATE ioctl function. The mark is checked for all ioctls
that specify the group handle and so userspace won't be abe to delete
a group that isn't marked yet.

v2: Add R-bs and fixes tags

## References
- https://git.kernel.org/stable/c/c646ebff3fa571e7ea974235286fb9ed3edc260c
- https://git.kernel.org/stable/c/deb8b2491f6b9882ae02d7dc2651c7bf4f3b7e05
- https://git.kernel.org/stable/c/eec7e23d848d2194dd8791fcd0f4a54d4378eecd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68735.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68735
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
