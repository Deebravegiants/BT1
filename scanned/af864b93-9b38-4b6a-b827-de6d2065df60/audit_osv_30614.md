# [H] iommu/s390: Implement blocking domain

## Summary
Severity: High
Advisory: CVE-2024-53232
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53232
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/s390: Implement blocking domain

This fixes a crash when surprise hot-unplugging a PCI device. This crash
happens because during hot-unplug __iommu_group_set_domain_nofail()
attaching the default domain fails when the platform no longer
recognizes the device as it has already been removed and we end up with
a NULL domain pointer and UAF. This is exactly the case referred to in
the second comment in __iommu_device_set_domain() and just as stated
there if we can instead attach the blocking domain the UAF is prevented
as this can handle the already removed device. Implement the blocking
domain to use this handling.  With this change, the crash is fixed but
we still hit a warning attempting to change DMA ownership on a blocked
device.

## References
- https://git.kernel.org/stable/c/3be34fa1cdbf180c1a948cfededfdf2cdc497199
- https://git.kernel.org/stable/c/bd89d94f3ea6fdaee983cbc69226a00b9bde6d59
- https://git.kernel.org/stable/c/ecda483339a5151e3ca30d6b82691ef6f1d17912
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53232.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53232
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
