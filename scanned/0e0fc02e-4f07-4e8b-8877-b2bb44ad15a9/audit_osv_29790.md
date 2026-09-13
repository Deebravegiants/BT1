# [H] PCI: Add missing bridge lock to pci_bus_lock()

## Summary
Severity: High
Advisory: CVE-2024-46750
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46750
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <4.19.322, >=4.20.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: Add missing bridge lock to pci_bus_lock()

One of the true positives that the cfg_access_lock lockdep effort
identified is this sequence:

  WARNING: CPU: 14 PID: 1 at drivers/pci/pci.c:4886 pci_bridge_secondary_bus_reset+0x5d/0x70
  RIP: 0010:pci_bridge_secondary_bus_reset+0x5d/0x70
  Call Trace:
   <TASK>
   ? __warn+0x8c/0x190
   ? pci_bridge_secondary_bus_reset+0x5d/0x70
   ? report_bug+0x1f8/0x200
   ? handle_bug+0x3c/0x70
   ? exc_invalid_op+0x18/0x70
   ? asm_exc_invalid_op+0x1a/0x20
   ? pci_bridge_secondary_bus_reset+0x5d/0x70
   pci_reset_bus+0x1d8/0x270
   vmd_probe+0x778/0xa10
   pci_device_probe+0x95/0x120

Where pci_reset_bus() users are triggering unlocked secondary bus resets.
Ironically pci_bus_reset(), several calls down from pci_reset_bus(), uses
pci_bus_lock() before issuing the reset which locks everything *but* the
bridge itself.

For the same motivation as adding:

  bridge = pci_upstream_bridge(dev);
  if (bridge)
    pci_dev_lock(bridge);

to pci_reset_function() for the "bus" and "cxl_bus" reset cases, add
pci_dev_lock() for @bus->self to pci_bus_lock().

[bhelgaas: squash in recursive locking deadlock fix from Keith Busch:
https://lore.kernel.org/r/20240711193650.701834-1-kbusch@meta.com]

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://git.kernel.org/stable/c/04e85a3285b0e5c5af6fd2c0fd6e95ffecc01945
- https://git.kernel.org/stable/c/0790b89c7e911003b8c50ae50e3ac7645de1fae9
- https://git.kernel.org/stable/c/7253b4fed46471cc247c6cacefac890a8472c083
- https://git.kernel.org/stable/c/78c6e39fef5c428960aff742149bba302dd46f5a
- https://git.kernel.org/stable/c/81c68e218ab883dfa368460a59b674084c0240da
- https://git.kernel.org/stable/c/a4e772898f8bf2e7e1cf661a12c60a5612c4afab
- https://git.kernel.org/stable/c/df77a678c33871a6e4ac5b54a71662f1d702335b
- https://git.kernel.org/stable/c/e2355d513b89a2cb511b4ded0deb426cdb01acd0
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46750.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46750
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
