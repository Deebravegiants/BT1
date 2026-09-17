# [H] Bluetooth: btusb: reorder cleanup in btusb_disconnect to avoid UAF

## Summary
Severity: High
Advisory: CVE-2025-40283
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-06
Source: https://osv.dev/vulnerability/CVE-2025-40283
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.4.302, >=5.5.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.59, >=6.13.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: btusb: reorder cleanup in btusb_disconnect to avoid UAF

There is a KASAN: slab-use-after-free read in btusb_disconnect().
Calling "usb_driver_release_interface(&btusb_driver, data->intf)" will
free the btusb data associated with the interface. The same data is
then used later in the function, hence the UAF.

Fix by moving the accesses to btusb data to before the data is free'd.

## References
- https://git.kernel.org/stable/c/1c28c1e1522c773a94e26950ffb145e88cd9834b
- https://git.kernel.org/stable/c/23d22f2f71768034d6ef86168213843fc49bf550
- https://git.kernel.org/stable/c/297dbf87989e09af98f81f2bcb938041785557e8
- https://git.kernel.org/stable/c/5dc00065a0496c36694afe11e52a5bc64524a9b8
- https://git.kernel.org/stable/c/7a6d1e740220ff9dfcb6a8c994d6ba49e76db198
- https://git.kernel.org/stable/c/95b9b98c93b1c0916a3d4cf4540b7f5d69145a0d
- https://git.kernel.org/stable/c/a2610ecd9fd5708be8997ca8f033e4200c0bb6af
- https://git.kernel.org/stable/c/f858f004bc343a7ae9f2533bbb2a3ab27428532f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40283.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40283
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
