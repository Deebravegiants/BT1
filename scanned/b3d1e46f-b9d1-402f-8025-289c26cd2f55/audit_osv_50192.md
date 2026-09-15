# [M] CVE-2019-9213

## Summary
Severity: Medium
Advisory: CVE-2019-9213
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-05
Source: https://osv.dev/vulnerability/CVE-2019-9213
Type: osv

## Details
In the Linux kernel before 4.20.14, expand_downwards in mm/mmap.c lacks a check for the mmap minimum address, which makes it easier for attackers to exploit kernel NULL pointer dereferences on non-SMAP platforms. This is related to a capability check for the wrong task.

## References
- https://usn.ubuntu.com/3931-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00045.html
- http://www.securityfocus.com/bid/107296
- https://usn.ubuntu.com/3932-1/
- https://usn.ubuntu.com/3933-1/
- https://access.redhat.com/errata/RHSA-2019:0831
- https://access.redhat.com/errata/RHSA-2019:1479
- https://usn.ubuntu.com/3930-1/
- https://usn.ubuntu.com/3930-2/
- https://usn.ubuntu.com/3931-2/
- https://usn.ubuntu.com/3932-2/
- https://usn.ubuntu.com/3933-2/
- https://access.redhat.com/errata/RHSA-2019:1480
- https://lists.debian.org/debian-lts-announce/2019/05/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00052.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.105
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.14
- https://github.com/torvalds/linux/commit/0a1d52994d440e21def1c2174932410b4f2a98a1
