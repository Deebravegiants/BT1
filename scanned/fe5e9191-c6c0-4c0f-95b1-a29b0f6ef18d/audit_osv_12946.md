# [M] CVE-2018-16435

## Summary
Severity: Medium
Advisory: CVE-2018-16435
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-16435
Type: osv

## Details
Little CMS (aka Little Color Management System) 2.9 has an integer overflow in the AllocateDataSet function in cmscgats.c, leading to a heap-based buffer overflow in the SetData function via a crafted file in the second argument to cmsIT8LoadFromFile.

## References
- https://access.redhat.com/errata/RHSA-2018:3004
- https://lists.debian.org/debian-lts-announce/2018/09/msg00005.html
- https://security.gentoo.org/glsa/202105-18
- https://usn.ubuntu.com/3770-1/
- https://usn.ubuntu.com/3770-2/
- https://www.debian.org/security/2018/dsa-4284
- https://github.com/mm2/Little-CMS/commit/768f70ca405cd3159d990e962d54456773bb8cf8
- https://github.com/mm2/Little-CMS/issues/171
