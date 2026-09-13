# [M] MIPS: Loongson64: DTS: Really fix PCIe port nodes for ls7a

## Summary
Severity: Medium
Advisory: CVE-2024-56785
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-56785
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

MIPS: Loongson64: DTS: Really fix PCIe port nodes for ls7a

Fix the dtc warnings:

    arch/mips/boot/dts/loongson/ls7a-pch.dtsi:68.16-416.5: Warning (interrupt_provider): /bus@10000000/pci@1a000000: '#interrupt-cells' found, but node is not an interrupt provider
    arch/mips/boot/dts/loongson/ls7a-pch.dtsi:68.16-416.5: Warning (interrupt_provider): /bus@10000000/pci@1a000000: '#interrupt-cells' found, but node is not an interrupt provider
    arch/mips/boot/dts/loongson/loongson64g_4core_ls7a.dtb: Warning (interrupt_map): Failed prerequisite 'interrupt_provider'

And a runtime warning introduced in commit 045b14ca5c36 ("of: WARN on
deprecated #address-cells/#size-cells handling"):

    WARNING: CPU: 0 PID: 1 at drivers/of/base.c:106 of_bus_n_addr_cells+0x9c/0xe0
    Missing '#address-cells' in /bus@10000000/pci@1a000000/pci_bridge@9,0

The fix is similar to commit d89a415ff8d5 ("MIPS: Loongson64: DTS: Fix PCIe
port nodes for ls7a"), which has fixed the issue for ls2k (despite its
subject mentions ls7a).

## References
- https://git.kernel.org/stable/c/01575f2ff8ba578a3436f230668bd056dc2eb823
- https://git.kernel.org/stable/c/4fbd66d8254cedfd1218393f39d83b6c07a01917
- https://git.kernel.org/stable/c/5a2eaa3ad2b803c7ea442c6db7379466ee73c024
- https://git.kernel.org/stable/c/8ef9ea1503d0a129cc6f5cf48fb63633efa5d766
- https://git.kernel.org/stable/c/a7fd78075031871bc68fc56fdaa6e7a3934064b1
- https://git.kernel.org/stable/c/c8ee41fc3522c6659e324d90bc2ccd3b6310d7fc
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56785.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56785
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
