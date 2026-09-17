# [M] CVE-2019-19947

## Summary
Severity: Medium
Advisory: CVE-2019-19947
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-12-24
Source: https://osv.dev/vulnerability/CVE-2019-19947
Type: osv

## Details
In the Linux kernel through 5.4.6, there are information leaks of uninitialized memory to a USB device in the drivers/net/can/usb/kvaser_usb/kvaser_usb_leaf.c driver, aka CID-da2311a6385c.

## References
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://usn.ubuntu.com/4284-1/
- https://usn.ubuntu.com/4285-1/
- https://usn.ubuntu.com/4427-1/
- https://usn.ubuntu.com/4485-1/
- http://www.openwall.com/lists/oss-security/2019/12/24/1
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://security.netapp.com/advisory/ntap-20200204-0002/
- https://github.com/torvalds/linux/commit/da2311a6385c3b499da2ed5d9be59ce331fa93e9
