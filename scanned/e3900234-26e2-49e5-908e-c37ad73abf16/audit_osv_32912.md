# [H] hisi_acc_vfio_pci: bugfix live migration function without VF device driver

## Summary
Severity: High
Advisory: CVE-2025-38283
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38283
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

hisi_acc_vfio_pci: bugfix live migration function without VF device driver

If the VF device driver is not loaded in the Guest OS and we attempt to
perform device data migration, the address of the migrated data will
be NULL.
The live migration recovery operation on the destination side will
access a null address value, which will cause access errors.

Therefore, live migration of VMs without added VF device drivers
does not require device data migration.
In addition, when the queue address data obtained by the destination
is empty, device queue recovery processing will not be performed.

## References
- https://git.kernel.org/stable/c/2777a40998deb36f96b6afc48bd397cf58a4edf0
- https://git.kernel.org/stable/c/53e8e8e909f7c3a77857d09d2b733a42547f57ee
- https://git.kernel.org/stable/c/59a834592dd200969fdf3c61be1cb0615c647e45
- https://git.kernel.org/stable/c/b5ef128926cd34dffa2a66607b9c82b902581ef8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38283.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38283
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
