# [H] iommu: Fix WARN_ON in __iommu_group_set_domain_nofail() due to reset

## Summary
Severity: High
Advisory: CVE-2026-52952
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52952
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu: Fix WARN_ON in __iommu_group_set_domain_nofail() due to reset

In __iommu_group_set_domain_internal(), concurrent domain attachments are
rejected when any device in the group is recovering. This is necessary to
fence concurrent attachments to a multi-device group where devices might
share the same RID due to PCI DMA alias quirks, but triggers the WARN_ON in
__iommu_group_set_domain_nofail().

Other IOMMU_SET_DOMAIN_MUST_SUCCEED callers in detach/teardown paths, such
as __iommu_group_set_core_domain and __iommu_release_dma_ownership, should
not be rejected, as the domain would be freed anyway in these nofail paths
while group->domain is still pointing to it. So pci_dev_reset_iommu_done()
could trigger a UAF when re-attaching group->domain.

Honor the IOMMU_SET_DOMAIN_MUST_SUCCEED flag, allowing the callers through
the group->recovery_cnt fence, so as to update the group->domain pointer.
Instead add a gdev->blocked check in the device iteration loop, to prevent
any concurrent per-device detachment.

## References
- https://git.kernel.org/stable/c/5474e6e17a262db45c60575c73f70210f5c7001f
- https://git.kernel.org/stable/c/8fc289e809f3eb7e36cadc4684ab6fad747a5a93
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-52952.json
- https://access.redhat.com/security/cve/CVE-2026-52952
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52952.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52952
- https://bugzilla.redhat.com/show_bug.cgi?id=2492422
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
