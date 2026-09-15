# [M] PCI/MSI: Handle lack of irqdomain gracefully

## Summary
Severity: Medium
Advisory: CVE-2024-56760
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2024-56760
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.69, >=6.7.0 <6.12.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI/MSI: Handle lack of irqdomain gracefully

Alexandre observed a warning emitted from pci_msi_setup_msi_irqs() on a
RISCV platform which does not provide PCI/MSI support:

 WARNING: CPU: 1 PID: 1 at drivers/pci/msi/msi.h:121 pci_msi_setup_msi_irqs+0x2c/0x32
 __pci_enable_msix_range+0x30c/0x596
 pci_msi_setup_msi_irqs+0x2c/0x32
 pci_alloc_irq_vectors_affinity+0xb8/0xe2

RISCV uses hierarchical interrupt domains and correctly does not implement
the legacy fallback. The warning triggers from the legacy fallback stub.

That warning is bogus as the PCI/MSI layer knows whether a PCI/MSI parent
domain is associated with the device or not. There is a check for MSI-X,
which has a legacy assumption. But that legacy fallback assumption is only
valid when legacy support is enabled, but otherwise the check should simply
return -ENOTSUPP.

Loongarch tripped over the same problem and blindly enabled legacy support
without implementing the legacy fallbacks. There are weak implementations
which return an error, so the problem was papered over.

Correct pci_msi_domain_supports() to evaluate the legacy mode and add
the missing supported check into the MSI enable path to complete it.

## References
- https://git.kernel.org/stable/c/a60b990798eb17433d0283788280422b1bd94b18
- https://git.kernel.org/stable/c/aed157301c659a48f5564cc4568cf0e5c8831af0
- https://git.kernel.org/stable/c/b1f7476e07b93d65a1a3643dcb4a7bed80d4328d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56760.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56760
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
