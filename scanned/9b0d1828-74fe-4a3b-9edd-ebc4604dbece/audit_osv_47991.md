# [M] CVE-2017-16535

## Summary
Severity: Medium
Advisory: CVE-2017-16535
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-04
Source: https://osv.dev/vulnerability/CVE-2017-16535
Type: osv

## Details
The usb_get_bos_descriptor function in drivers/usb/core/config.c in the Linux kernel before 4.13.10 allows local users to cause a denial of service (out-of-bounds read and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- http://www.securityfocus.com/bid/102022
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3754-1/
- https://groups.google.com/d/msg/syzkaller/tzdz2fTB1K0/OvjIgLSTAgAJ
- https://github.com/torvalds/linux/commit/1c0edc3633b56000e18d82fc241e3995ca18a69e
