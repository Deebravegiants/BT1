# [M] CVE-2021-46909

## Summary
Severity: Medium
Advisory: CVE-2021-46909
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46909
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ARM: footbridge: fix PCI interrupt mapping

Since commit 30fdfb929e82 ("PCI: Add a call to pci_assign_irq() in
pci_device_probe()"), the PCI code will call the IRQ mapping function
whenever a PCI driver is probed. If these are marked as __init, this
causes an oops if a PCI driver is loaded or bound after the kernel has
initialised.

## References
- https://git.kernel.org/stable/c/871b569a3e67f570df9f5ba195444dc7c621293b
- https://git.kernel.org/stable/c/c3efce8cc9807339633ee30e39882f4c8626ee1d
- https://git.kernel.org/stable/c/1fc087fdb98d556b416c82ed6e3964a30885f47a
- https://git.kernel.org/stable/c/2643da6aa57920d9159a1a579fb04f89a2b0d29a
- https://git.kernel.org/stable/c/30e3b4f256b4e366a61658c294f6a21b8626dda7
- https://git.kernel.org/stable/c/532747fd5c7aaa17ee5cf79f3e947c31eb0e35cf
