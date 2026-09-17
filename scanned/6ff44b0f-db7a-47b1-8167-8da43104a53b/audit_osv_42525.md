# [H] usb: core: sysfs: add lock to bos_descriptors_read()

## Summary
Severity: High
Advisory: CVE-2026-68374
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68374
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: core: sysfs: add lock to bos_descriptors_read()

Add a lock to the function bos_descriptors_read().

This function accesses udev->bos, which could be simultaneously freed in
usb_reset_and_verify_device(), a function that is commonly called in
drivers all over the kernel.

## References
- https://git.kernel.org/stable/c/217774e143d7b5a88739193284b6421be3978601
- https://git.kernel.org/stable/c/4e0197fbb0eec588795d5431716a244d9ac8fa93
- https://git.kernel.org/stable/c/ab82adf5e63b2d89ead7933ab753b9cedbe028e9
- https://git.kernel.org/stable/c/c07caee449c968842a350bfefa049889923b8240
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68374.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68374
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
