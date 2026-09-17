# [H] iommu: Restore lost return in iommu_report_device_fault()

## Summary
Severity: High
Advisory: CVE-2024-44994
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44994
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu: Restore lost return in iommu_report_device_fault()

When iommu_report_device_fault gets called with a partial fault it is
supposed to collect the fault into the group and then return.

Instead the return was accidently deleted which results in trying to
process the fault and an eventual crash.

Deleting the return was a typo, put it back.

## References
- https://git.kernel.org/stable/c/cc6bc2ab1663ec9353636416af22452b078510e9
- https://git.kernel.org/stable/c/fca5b78511e98bdff2cdd55c172b23200a7b3404
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44994.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44994
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
