# [M] CVE-2018-16062

## Summary
Severity: Medium
Advisory: CVE-2018-16062
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-29
Source: https://osv.dev/vulnerability/CVE-2018-16062
Type: osv

## Details
dwarf_getaranges in dwarf_getaranges.c in libdw in elfutils before 2018-08-18 allows remote attackers to cause a denial of service (heap-based buffer over-read) via a crafted file.

## References
- https://sourceware.org/git/?p=elfutils.git%3Ba=commit%3Bh=29e31978ba51c1051743a503ee325b5ebc03d7e9
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00052.html
- https://access.redhat.com/errata/RHSA-2019:2197
- https://lists.debian.org/debian-lts-announce/2019/02/msg00036.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00030.html
- https://usn.ubuntu.com/4012-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23541
