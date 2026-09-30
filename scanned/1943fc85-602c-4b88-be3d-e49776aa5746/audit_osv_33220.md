# [H] drm/amd/display: remove oem i2c adapter on finish

## Summary
Severity: High
Advisory: CVE-2025-39906
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39906
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: remove oem i2c adapter on finish

Fixes a bug where unbinding of the GPU would leave the oem i2c adapter
registered resulting in a null pointer dereference when applications try
to access the invalid device.

(cherry picked from commit 89923fb7ead4fdd37b78dd49962d9bb5892403e6)

## References
- https://git.kernel.org/stable/c/1dfd2864a1c4909147663e5a27c055f50f7c2796
- https://git.kernel.org/stable/c/c686124bcf06253620790857ff462f00f3f7a4ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39906.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39906
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
