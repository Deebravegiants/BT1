# [H] PCI: endpoint: Fix PCI domain ID release in pci_epc_destroy()

## Summary
Severity: High
Advisory: CVE-2024-56561
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56561
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: endpoint: Fix PCI domain ID release in pci_epc_destroy()

pci_epc_destroy() invokes pci_bus_release_domain_nr() to release the PCI
domain ID, but there are two issues:

  - 'epc->dev' is passed to pci_bus_release_domain_nr() which was already
    freed by device_unregister(), leading to a use-after-free issue.

  - Domain ID corresponds to the EPC device parent, so passing 'epc->dev'
    is also wrong.

Fix these issues by passing 'epc->dev.parent' to
pci_bus_release_domain_nr() and also do it before device_unregister().

[mani: reworded subject and description]

## References
- https://git.kernel.org/stable/c/4acc902ed3743edd4ac2d3846604a99d17104359
- https://git.kernel.org/stable/c/c74a1df6c2a2df7dd45c3fc1a5edc29a075dcf22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56561.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56561
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
