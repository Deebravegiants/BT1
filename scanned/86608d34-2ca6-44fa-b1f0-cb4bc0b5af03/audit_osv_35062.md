# [H] drm/radeon: Do not kfree() devres managed rdev

## Summary
Severity: High
Advisory: CVE-2025-68170
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68170
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/radeon: Do not kfree() devres managed rdev

Since the allocation of the drivers main structure was changed to
devm_drm_dev_alloc() rdev is managed by devres and we shouldn't be calling
kfree() on it.

This fixes things exploding if the driver probe fails and devres cleans up
the rdev after we already free'd it.

(cherry picked from commit 16c0681617b8a045773d4d87b6140002fa75b03b)

## References
- https://git.kernel.org/stable/c/2413bbd1d692aed245c2aa38a369a1fa7590db84
- https://git.kernel.org/stable/c/3328443363a0895fd9c096edfe8ecd372ca9145e
- https://git.kernel.org/stable/c/f7482516002a11317912e29577bbf33cf59a0fb1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68170.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68170
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
