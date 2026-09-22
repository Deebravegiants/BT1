# [M] CVE-2017-16532

## Summary
Severity: Medium
Advisory: CVE-2017-16532
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-04
Source: https://osv.dev/vulnerability/CVE-2017-16532
Type: osv

## Details
The get_endpoints function in drivers/usb/misc/usbtest.c in the Linux kernel through 4.13.11 allows local users to cause a denial of service (NULL pointer dereference and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- https://usn.ubuntu.com/3754-1/
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3619-2/
- https://groups.google.com/d/msg/syzkaller/l3870gs3LhA/y79DYQdFBAAJ
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3617-1/
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3617-3/
- https://github.com/torvalds/linux/commit/7c80f9e4a588f1925b07134bb2e3689335f6c6d8
