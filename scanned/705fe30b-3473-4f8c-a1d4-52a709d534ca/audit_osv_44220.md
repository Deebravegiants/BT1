# [H] accel/amdxdna: Fix iommu domain lifetime race during device removal

## Summary
Severity: High
Advisory: CVE-2026-80608
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80608
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/amdxdna: Fix iommu domain lifetime race during device removal

When force_iova mode is enabled, amdxdna_remove() frees xdna->domain. If
amdxdna_gem_obj_free() is called after device removal, it may attempt to
access xdna->domain, resulting in a use-after-free.

Fix the race by adding freeing xdna->domain as a managed release action,
so its lifetime is managed by DRM and remains valid until all managed
resources are released.

## References
- https://git.kernel.org/stable/c/65e7e2b8d71b418439ebc68e80ed3e5a325375d6
- https://git.kernel.org/stable/c/b4a0500fdf6e61a6c5f92ff2e61bc91578075803
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80608.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80608
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
