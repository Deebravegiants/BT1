# [H] iommu/vt-d: Fix incorrect pci_for_each_dma_alias() for non-PCI devices

## Summary
Severity: High
Advisory: CVE-2024-50101
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50101
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.169, >=5.16.0 <6.1.114, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Fix incorrect pci_for_each_dma_alias() for non-PCI devices

Previously, the domain_context_clear() function incorrectly called
pci_for_each_dma_alias() to set up context entries for non-PCI devices.
This could lead to kernel hangs or other unexpected behavior.

Add a check to only call pci_for_each_dma_alias() for PCI devices. For
non-PCI devices, domain_context_clear_one() is called directly.

## References
- https://git.kernel.org/stable/c/04d6826ba7ba81213422276e96c90c6565169e1c
- https://git.kernel.org/stable/c/0bd9a30c22afb5da203386b811ec31429d2caa78
- https://git.kernel.org/stable/c/6e02a277f1db24fa039e23783c8921c7b0e5b1b3
- https://git.kernel.org/stable/c/cbfa3a83eba05240ce37839ed48280a05e8e8f6c
- https://git.kernel.org/stable/c/fe2e0b6cd00abea3efac66de1da22d844364c1b0
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50101.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50101
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
