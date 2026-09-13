# [M] CVE-2018-16403

## Summary
Severity: Medium
Advisory: CVE-2018-16403
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-03
Source: https://osv.dev/vulnerability/CVE-2018-16403
Type: osv

## Details
libdw in elfutils 0.173 checks the end of the attributes list incorrectly in dwarf_getabbrev in dwarf_getabbrev.c and dwarf_hasattr in dwarf_hasattr.c, leading to a heap-based buffer over-read and an application crash.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00052.html
- https://sourceware.org/git/?p=elfutils.git%3Ba=commit%3Bh=6983e59b727458a6c64d9659c85f08218bc4fcda
- https://usn.ubuntu.com/4012-1/
- https://access.redhat.com/errata/RHSA-2019:2197
- https://sourceware.org/bugzilla/show_bug.cgi?id=23529
