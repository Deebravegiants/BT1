# [M] misc: microchip: pci1xxxx: Resolve kernel panic during GPIO IRQ handling

## Summary
Severity: Medium
Advisory: CVE-2024-57916
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2024-57916
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.125, >=6.2.0 <6.6.72, >=6.7.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: microchip: pci1xxxx: Resolve kernel panic during GPIO IRQ handling

Resolve kernel panic caused by improper handling of IRQs while
accessing GPIO values. This is done by replacing generic_handle_irq with
handle_nested_irq.

## References
- https://git.kernel.org/stable/c/194f9f94a5169547d682e9bbcc5ae6d18a564735
- https://git.kernel.org/stable/c/25692750c0259c5b65afec467d97201a485e8a00
- https://git.kernel.org/stable/c/47d3749ec0cb56b7b98917c190a8c10cb54216fd
- https://git.kernel.org/stable/c/79aef6187e16b2d32307c8ff610e9e04f7f86e1f
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57916.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57916
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
