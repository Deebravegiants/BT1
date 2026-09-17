# [M] CVE-2018-11645

## Summary
Severity: Medium
Advisory: CVE-2018-11645
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-06-01
Source: https://osv.dev/vulnerability/CVE-2018-11645
Type: osv

## Details
psi/zfile.c in Artifex Ghostscript before 9.21rc1 permits the status command even if -dSAFER is used, which might allow remote attackers to determine the existence and size of arbitrary files, a similar issue to CVE-2016-7977.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=b60d50b7567369ad856cebe1efb6cd7dd2284219
- https://lists.debian.org/debian-lts-announce/2018/09/msg00015.html
- https://usn.ubuntu.com/3768-1/
- https://access.redhat.com/errata/RHSA-2019:2281
- https://www.debian.org/security/2018/dsa-4336
- https://bugs.ghostscript.com/show_bug.cgi?id=697193
