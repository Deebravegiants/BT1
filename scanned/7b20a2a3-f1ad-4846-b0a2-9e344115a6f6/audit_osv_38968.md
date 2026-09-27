# [H] PCI: Fix pci_slot_trylock() error handling

## Summary
Severity: High
Advisory: CVE-2026-43211
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43211
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.11.0 <6.18.16, >=6.13.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: Fix pci_slot_trylock() error handling

Commit a4e772898f8b ("PCI: Add missing bridge lock to pci_bus_lock()")
delegates the bridge device's pci_dev_trylock() to pci_bus_trylock() in
pci_slot_trylock(), but it forgets to remove the corresponding
pci_dev_unlock() when pci_bus_trylock() fails.

Before a4e772898f8b, the code did:

  if (!pci_dev_trylock(dev)) /* <- lock bridge device */
    goto unlock;
  if (dev->subordinate) {
    if (!pci_bus_trylock(dev->subordinate)) {
      pci_dev_unlock(dev);   /* <- unlock bridge device */
      goto unlock;
    }
  }

After a4e772898f8b the bridge-device lock is no longer taken, but the
pci_dev_unlock(dev) on the failure path was left in place, leading to the
bug.

This yields one of two errors:

  1. A warning that the lock is being unlocked when no one holds it.
  2. An incorrect unlock of a lock that belongs to another thread.

Fix it by removing the now-redundant pci_dev_unlock(dev) on the failure
path.

[Same patch later posted by Keith at
https://patch.msgid.link/20260116184150.3013258-1-kbusch@meta.com]

## References
- https://git.kernel.org/stable/c/0425aaf20b407d2f2cf3bf469808e4a35f9abb8b
- https://git.kernel.org/stable/c/8b08ea9690b212b7bf7f12414039259cf34b1aa0
- https://git.kernel.org/stable/c/9368d1ee62829b08aa31836b3ca003803caf0b72
- https://git.kernel.org/stable/c/943ed56606a7ab2fe5a99cad572dd17d484310c7
- https://git.kernel.org/stable/c/a19b61fdb958ffadbba85b43c991eb9fc70c1c1c
- https://git.kernel.org/stable/c/bd435f4b738130d732ef64e0e57e45185f77165d
- https://git.kernel.org/stable/c/ebb27b7399ab8b9eb1f792b329aa5f6250c590d4
- https://git.kernel.org/stable/c/fbe06a3058114bf95a17a4941b205f4b321c6f0a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43211.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43211
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
