# [M] CVE-2017-16643

## Summary
Severity: Medium
Advisory: CVE-2017-16643
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-16643
Type: osv

## Details
The parse_hid_report_descriptor function in drivers/input/tablet/gtco.c in the Linux kernel before 4.13.11 allows local users to cause a denial of service (out-of-bounds read and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3754-1/
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.11
- http://www.securityfocus.com/bid/101769
- https://groups.google.com/d/msg/syzkaller/McWFcOsA47Y/3bjtBBgaBAAJ
- https://github.com/torvalds/linux/commit/a50829479f58416a013a4ccca791336af3c584c7
