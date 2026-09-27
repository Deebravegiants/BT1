# [M] PCI/bwctrl: Fix NULL pointer dereference on bus number exhaustion

## Summary
Severity: Medium
Advisory: CVE-2025-22031
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22031
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI/bwctrl: Fix NULL pointer dereference on bus number exhaustion

When BIOS neglects to assign bus numbers to PCI bridges, the kernel
attempts to correct that during PCI device enumeration.  If it runs out
of bus numbers, no pci_bus is allocated and the "subordinate" pointer in
the bridge's pci_dev remains NULL.

The PCIe bandwidth controller erroneously does not check for a NULL
subordinate pointer and dereferences it on probe.

Bandwidth control of unusable devices below the bridge is of questionable
utility, so simply error out instead.  This mirrors what PCIe hotplug does
since commit 62e4492c3063 ("PCI: Prevent NULL dereference during pciehp
probe").

The PCI core emits a message with KERN_INFO severity if it has run out of
bus numbers.  PCIe hotplug emits an additional message with KERN_ERR
severity to inform the user that hotplug functionality is disabled at the
bridge.  A similar message for bandwidth control does not seem merited,
given that its only purpose so far is to expose an up-to-date link speed
in sysfs and throttle the link speed on certain laptops with limited
Thermal Design Power.  So error out silently.

User-visible messages:

  pci 0000:16:02.0: bridge configuration invalid ([bus 00-00]), reconfiguring
  [...]
  pci_bus 0000:45: busn_res: [bus 45-74] end is updated to 74
  pci 0000:16:02.0: devices behind bridge are unusable because [bus 45-74] cannot be assigned for them
  [...]
  pcieport 0000:16:02.0: pciehp: Hotplug bridge without secondary bus, ignoring
  [...]
  BUG: kernel NULL pointer dereference
  RIP: pcie_update_link_speed
  pcie_bwnotif_enable
  pcie_bwnotif_probe
  pcie_port_probe_service
  really_probe

## References
- https://git.kernel.org/stable/c/1181924af78e5299ddec6e457789c02dd5966559
- https://git.kernel.org/stable/c/667f053b05f00a007738cd7ed6fa1901de19dc7e
- https://git.kernel.org/stable/c/d93d309013e89631630a12b1770d27e4be78362a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22031.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22031
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
