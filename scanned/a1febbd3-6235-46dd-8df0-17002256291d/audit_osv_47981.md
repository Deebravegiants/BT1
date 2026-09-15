# [M] CVE-2017-16525

## Summary
Severity: Medium
Advisory: CVE-2017-16525
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-04
Source: https://osv.dev/vulnerability/CVE-2017-16525
Type: osv

## Details
The usb_serial_console_disconnect function in drivers/usb/serial/console.c in the Linux kernel before 4.13.8 allows local users to cause a denial of service (use-after-free and system crash) or possibly have unspecified other impact via a crafted USB device, related to disconnection and failed setup.

## References
- http://www.securityfocus.com/bid/102028
- https://groups.google.com/d/msg/syzkaller/cMACrmo1x0k/4KhRoUgABAAJ
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3583-1/
- https://usn.ubuntu.com/3583-2/
- https://github.com/torvalds/linux/commit/299d7572e46f98534033a9e65973f13ad1ce9047
- https://github.com/torvalds/linux/commit/bd998c2e0df0469707503023d50d46cf0b10c787
