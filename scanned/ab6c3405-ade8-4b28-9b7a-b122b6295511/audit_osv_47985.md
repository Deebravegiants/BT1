# [M] CVE-2017-16529

## Summary
Severity: Medium
Advisory: CVE-2017-16529
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-04
Source: https://osv.dev/vulnerability/CVE-2017-16529
Type: osv

## Details
The snd_usb_create_streams function in sound/usb/card.c in the Linux kernel before 4.13.6 allows local users to cause a denial of service (out-of-bounds read and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3754-1/
- http://www.securityfocus.com/bid/103284
- https://groups.google.com/d/msg/syzkaller/rDzv5RP_f2M/M5au06qmAwAJ
- https://github.com/torvalds/linux/commit/bfc81a8bc18e3c4ba0cbaa7666ff76be2f998991
