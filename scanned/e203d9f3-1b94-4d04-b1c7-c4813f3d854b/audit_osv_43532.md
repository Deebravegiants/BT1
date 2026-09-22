# [H] iommufd: Destroy the pages content after detaching from dmabuf

## Summary
Severity: High
Advisory: CVE-2026-74328
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74328
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommufd: Destroy the pages content after detaching from dmabuf

Sashiko points out this has gotten out of order, the mutex could still be
in use through the dmabuf invalidation callbacks. Don't destroy any of the
pages content until the dmabuf is fully detached.

## References
- https://git.kernel.org/stable/c/0507fcedbdcc87281ef8639c045fc9980363bbb6
- https://git.kernel.org/stable/c/f2d70dbd3dcefa8e3c380beff9c31f5f033a4221
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74328.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74328
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
