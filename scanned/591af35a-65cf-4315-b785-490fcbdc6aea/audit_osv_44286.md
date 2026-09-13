# [H] ata: pata_sl82c105: fix bridge revision use-after-free

## Summary
Severity: High
Advisory: CVE-2026-80732
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80732
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.23 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ata: pata_sl82c105: fix bridge revision use-after-free

pci_get_slot() returns a referenced PCI device. Commit 44c10138fd4b
("PCI: Change all drivers to use pci_device->revision") replaced a
configuration-space read with direct access to the cached revision field,
but left that access after pci_dev_put(). The bridge may therefore be freed
before its revision is read.

Read the revision before dropping the reference.

## References
- https://git.kernel.org/stable/c/1268ca9418e2217f2b60705cf4a280b689b26678
- https://git.kernel.org/stable/c/56fd78c8c820f527f8003e379ab71004b2e79a44
- https://git.kernel.org/stable/c/5ef87b1b4656d675440ceab32a56e69ad958d3a1
- https://git.kernel.org/stable/c/7700a31039cdc6715cb6cce7e7a664ee4e945f67
- https://git.kernel.org/stable/c/a626dfca96041842053cf2d1efceb436c4cd8dcf
- https://git.kernel.org/stable/c/a837deeaa37cc3f0e8c4e5c096787047f272c956
- https://git.kernel.org/stable/c/dc711fb137b33c12e6ca22b6a9c9b9f21d49e4de
- https://git.kernel.org/stable/c/fa0dca89b4fb0909ffda7b9ab6051af33270f95e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80732.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80732
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
