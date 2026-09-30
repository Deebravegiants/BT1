# [H] drm/panthor: Fix race condition when gathering fdinfo group samples

## Summary
Severity: High
Advisory: CVE-2025-22100
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22100
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: Fix race condition when gathering fdinfo group samples

Commit e16635d88fa0 ("drm/panthor: add DRM fdinfo support") failed to
protect access to groups with an xarray lock, which could lead to
use-after-free errors.

## References
- https://git.kernel.org/stable/c/0590c94c3596d6c1a3d549ae611366f2ad4e1d8d
- https://git.kernel.org/stable/c/6d98c83ad67e7bd86a47494fd6c3863e7bb26db9
- https://git.kernel.org/stable/c/e9d45f42a64a400adba59ee83d03e6db662530b4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22100.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22100
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
