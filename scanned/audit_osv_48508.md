# [M] CVE-2017-8831

## Summary
Severity: Medium
Advisory: CVE-2017-8831
CVSS: 6.4 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-08
Source: https://osv.dev/vulnerability/CVE-2017-8831
Type: osv

## Details
The saa7164_bus_get function in drivers/media/pci/saa7164/saa7164-bus.c in the Linux kernel through 4.11.5 allows local users to cause a denial of service (out-of-bounds array access) or possibly have unspecified other impact by changing a certain sequence-number value, aka a "double fetch" vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3754-1/
- http://www.securityfocus.com/archive/1/540770/30/0/threaded
- http://www.securityfocus.com/bid/99619
- https://bugzilla.kernel.org/show_bug.cgi?id=195559
- https://github.com/stoth68000/media-tree/commit/354dd3924a2e43806774953de536257548b5002c
