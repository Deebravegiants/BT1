# [H] iommu/vt-d: Restore context entry setup order for aliased devices

## Summary
Severity: High
Advisory: CVE-2025-38216
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38216
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Restore context entry setup order for aliased devices

Commit 2031c469f816 ("iommu/vt-d: Add support for static identity domain")
changed the context entry setup during domain attachment from a
set-and-check policy to a clear-and-reset approach. This inadvertently
introduced a regression affecting PCI aliased devices behind PCIe-to-PCI
bridges.

Specifically, keyboard and touchpad stopped working on several Apple
Macbooks with below messages:

 kernel: platform pxa2xx-spi.3: Adding to iommu group 20
 kernel: input: Apple SPI Keyboard as
 /devices/pci0000:00/0000:00:1e.3/pxa2xx-spi.3/spi_master/spi2/spi-APP000D:00/input/input0
 kernel: DMAR: DRHD: handling fault status reg 3
 kernel: DMAR: [DMA Read NO_PASID] Request device [00:1e.3] fault addr
 0xffffa000 [fault reason 0x06] PTE Read access is not set
 kernel: DMAR: DRHD: handling fault status reg 3
 kernel: DMAR: [DMA Read NO_PASID] Request device [00:1e.3] fault addr
 0xffffa000 [fault reason 0x06] PTE Read access is not set
 kernel: applespi spi-APP000D:00: Error writing to device: 01 0e 00 00
 kernel: DMAR: DRHD: handling fault status reg 3
 kernel: DMAR: [DMA Read NO_PASID] Request device [00:1e.3] fault addr
 0xffffa000 [fault reason 0x06] PTE Read access is not set
 kernel: DMAR: DRHD: handling fault status reg 3
 kernel: applespi spi-APP000D:00: Error writing to device: 01 0e 00 00

Fix this by restoring the previous context setup order.

## References
- https://git.kernel.org/stable/c/320302baed05c6456164652541f23d2a96522c06
- https://git.kernel.org/stable/c/d43c81b691813e16a2d08208ce8947aebdab83cd
- https://git.kernel.org/stable/c/fb5873b779dd5858123c19bbd6959566771e2e83
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38216.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38216
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
