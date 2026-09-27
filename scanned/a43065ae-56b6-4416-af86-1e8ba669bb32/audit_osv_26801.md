# [H] iommufd: Do not add the same hwpt to the ioas->hwpt_list twice

## Summary
Severity: High
Advisory: CVE-2023-54043
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54043
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommufd: Do not add the same hwpt to the ioas->hwpt_list twice

The hwpt is added to the hwpt_list only during its creation, it is never
added again. This hunk is some missed leftover from rework. Adding it
twice will corrupt the linked list in some cases.

It effects HWPT specific attachment, which is something the test suite
cannot cover until we can create a legitimate struct device with a
non-system iommu "driver" (ie we need the bus removed from the iommu code)

## References
- https://git.kernel.org/stable/c/b4ff830eca097df51af10a9be29e8cc817327919
- https://git.kernel.org/stable/c/c44adefdcf472f946f0632f4e0ddcbf3e00b8516
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54043.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54043
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
