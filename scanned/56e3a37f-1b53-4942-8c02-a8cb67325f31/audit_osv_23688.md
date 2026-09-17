# [H] drm/etnaviv: check for reaped mapping in etnaviv_iommu_unmap_gem

## Summary
Severity: High
Advisory: CVE-2022-49336
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49336
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/etnaviv: check for reaped mapping in etnaviv_iommu_unmap_gem

When the mapping is already reaped the unmap must be a no-op, as we
would otherwise try to remove the mapping twice, corrupting the involved
data structures.

## References
- https://git.kernel.org/stable/c/03bd455a79f69d97fee3e3b212ab754442f10e5c
- https://git.kernel.org/stable/c/19323b3671a85788569d15685c8f83a05ec48cbb
- https://git.kernel.org/stable/c/436cff507f2a41230baacc3e2ef1d3b2d2653f40
- https://git.kernel.org/stable/c/461c0fdf9434188875da9f10cfc86065866bb797
- https://git.kernel.org/stable/c/64f4edec081cb7c97c5e928529d0e1b0dbbffb83
- https://git.kernel.org/stable/c/e168c25526cd0368af098095c2ded4a008007e1b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49336.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49336
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
