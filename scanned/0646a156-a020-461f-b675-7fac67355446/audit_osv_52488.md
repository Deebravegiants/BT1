# [M] CVE-2021-47503

## Summary
Severity: Medium
Advisory: CVE-2021-47503
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47503
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: pm80xx: Do not call scsi_remove_host() in pm8001_alloc()

Calling scsi_remove_host() before scsi_add_host() results in a crash:

 BUG: kernel NULL pointer dereference, address: 0000000000000108
 RIP: 0010:device_del+0x63/0x440
 Call Trace:
  device_unregister+0x17/0x60
  scsi_remove_host+0xee/0x2a0
  pm8001_pci_probe+0x6ef/0x1b90 [pm80xx]
  local_pci_probe+0x3f/0x90

We cannot call scsi_remove_host() in pm8001_alloc() because scsi_add_host()
has not been called yet at that point in time.

Function call tree:

  pm8001_pci_probe()
  |
  `- pm8001_pci_alloc()
  |  |
  |  `- pm8001_alloc()
  |     |
  |     `- scsi_remove_host()
  |
  `- scsi_add_host()

## References
- https://git.kernel.org/stable/c/653926205741add87a6cf452e21950eebc6ac10b
- https://git.kernel.org/stable/c/f8dccc1bdea7e21b5ec06c957aef8831c772661c
- https://git.kernel.org/stable/c/1e434d2687e8bc0b3cdc9dd093c0e9047c0b4add
