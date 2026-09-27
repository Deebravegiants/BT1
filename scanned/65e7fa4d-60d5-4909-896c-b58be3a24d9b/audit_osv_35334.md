# [H] Bluetooth: btusb: revert use of devm_kzalloc in btusb

## Summary
Severity: High
Advisory: CVE-2025-71082
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71082
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: btusb: revert use of devm_kzalloc in btusb

This reverts commit 98921dbd00c4e ("Bluetooth: Use devm_kzalloc in
btusb.c file").

In btusb_probe(), we use devm_kzalloc() to allocate the btusb data. This
ties the lifetime of all the btusb data to the binding of a driver to
one interface, INTF. In a driver that binds to other interfaces, ISOC
and DIAG, this is an accident waiting to happen.

The issue is revealed in btusb_disconnect(), where calling
usb_driver_release_interface(&btusb_driver, data->intf) will have devm
free the data that is also being used by the other interfaces of the
driver that may not be released yet.

To fix this, revert the use of devm and go back to freeing memory
explicitly.

## References
- https://git.kernel.org/stable/c/1e54c19eaf84ba652c4e376571093e58e144b339
- https://git.kernel.org/stable/c/252714f1e8bdd542025b16321c790458014d6880
- https://git.kernel.org/stable/c/c0ecb3e4451fe94f4315e6d09c4046dfbc42090b
- https://git.kernel.org/stable/c/cca0e9206e3bcc63cd3e72193e60149165d493cc
- https://git.kernel.org/stable/c/fdf7c640fb8a44a59b0671143d8c2f738bc48003
- https://git.kernel.org/stable/c/fff9206b0907252a41eb12b7c1407b9347df18b1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71082.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71082
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
