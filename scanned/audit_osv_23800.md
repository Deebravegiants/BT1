# [M] drm/msm: Fix null pointer dereferences without iommu

## Summary
Severity: Medium
Advisory: CVE-2022-49499
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49499
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm: Fix null pointer dereferences without iommu

Check if 'aspace' is set before using it as it will stay null without
IOMMU, such as on msm8974.

## References
- https://git.kernel.org/stable/c/36a1d1bda77e1851bddfa9cf4e8ada94476dbaff
- https://git.kernel.org/stable/c/f09937e80f9bc792965476c9a528f26c8fdc9179
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49499.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49499
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
