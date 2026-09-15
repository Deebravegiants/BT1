# [H] drm/amdgpu/vce: Prevent partial address patches

## Summary
Severity: High
Advisory: CVE-2026-53375
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53375
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu/vce: Prevent partial address patches

In the case that only one of lo/hi is valid, the patching could result
in a bad address written to in FW.

## References
- https://git.kernel.org/stable/c/0ee17150763962671f43a62ddf8f6ea1feaff438
- https://git.kernel.org/stable/c/2d66d1f5d8c0434e9a5ad21cc6eaf3a5e32141d5
- https://git.kernel.org/stable/c/944db9cfa5373f67eb94621d4c2eee572c05fa3f
- https://git.kernel.org/stable/c/b3d1a0a45c4aec484fa2a5b060b611e3d3064470
- https://git.kernel.org/stable/c/de2a02cc28d6d5d37db07d00a9a684c754a5fd74
- https://git.kernel.org/stable/c/ea2c554e700b86a04534b4c24ece5844e8c5f07e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53375.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53375
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
