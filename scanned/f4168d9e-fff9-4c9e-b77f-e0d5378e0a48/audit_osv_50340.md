# [M] CVE-2020-12771

## Summary
Severity: Medium
Advisory: CVE-2020-12771
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-09
Source: https://osv.dev/vulnerability/CVE-2020-12771
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.6.11. btree_gc_coalesce in drivers/md/bcache/btree.c has a deadlock if a coalescing operation fails.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://usn.ubuntu.com/4465-1/
- https://usn.ubuntu.com/4483-1/
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://usn.ubuntu.com/4462-1/
- https://usn.ubuntu.com/4463-1/
- https://usn.ubuntu.com/4485-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00071.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00009.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00019.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://lkml.org/lkml/2020/4/26/87
- https://www.oracle.com/security-alerts/cpuApr2021.html
