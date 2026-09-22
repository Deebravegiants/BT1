# [M] CVE-2017-16531

## Summary
Severity: Medium
Advisory: CVE-2017-16531
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-04
Source: https://osv.dev/vulnerability/CVE-2017-16531
Type: osv

## Details
drivers/usb/core/config.c in the Linux kernel before 4.13.6 allows local users to cause a denial of service (out-of-bounds read and system crash) or possibly have unspecified other impact via a crafted USB device, related to the USB_DT_INTERFACE_ASSOCIATION descriptor.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3754-1/
- http://www.securityfocus.com/bid/102025
- https://groups.google.com/d/msg/syzkaller/hP6L-m59m_8/Co2ouWeFAwAJ
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://github.com/torvalds/linux/commit/bd7a3fe770ebd8391d1c7d072ff88e9e76d063eb
