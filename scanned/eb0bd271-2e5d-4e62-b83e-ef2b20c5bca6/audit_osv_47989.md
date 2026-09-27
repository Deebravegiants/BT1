# [M] CVE-2017-16533

## Summary
Severity: Medium
Advisory: CVE-2017-16533
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-04
Source: https://osv.dev/vulnerability/CVE-2017-16533
Type: osv

## Details
The usbhid_parse function in drivers/hid/usbhid/hid-core.c in the Linux kernel before 4.13.8 allows local users to cause a denial of service (out-of-bounds read and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- http://www.securityfocus.com/bid/102026
- https://groups.google.com/d/msg/syzkaller/CxkJ9QZgwlM/O3IOvAaGAwAJ
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3754-1/
- https://github.com/torvalds/linux/commit/f043bfc98c193c284e2cd768fefabe18ac2fed9b
