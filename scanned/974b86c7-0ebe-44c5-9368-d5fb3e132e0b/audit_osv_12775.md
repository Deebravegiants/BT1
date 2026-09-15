# [H] CVE-2018-14681

## Summary
Severity: High
Advisory: CVE-2018-14681
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-28
Source: https://osv.dev/vulnerability/CVE-2018-14681
Type: osv

## Details
An issue was discovered in kwajd_read_headers in mspack/kwajd.c in libmspack before 0.7alpha. Bad KWAJ file header extensions could cause a one or two byte overwrite.

## References
- http://www.openwall.com/lists/oss-security/2018/07/26/1
- http://www.securitytracker.com/id/1041410
- https://access.redhat.com/errata/RHSA-2018:3327
- https://access.redhat.com/errata/RHSA-2018:3505
- https://lists.debian.org/debian-lts-announce/2018/08/msg00007.html
- https://security.gentoo.org/glsa/201903-20
- https://usn.ubuntu.com/3728-1/
- https://usn.ubuntu.com/3728-2/
- https://usn.ubuntu.com/3728-3/
- https://usn.ubuntu.com/3789-2/
- https://www.debian.org/security/2018/dsa-4260
- https://bugs.debian.org/904799
- https://github.com/kyz/libmspack/commit/0b0ef9344255ff5acfac6b7af09198ac9c9756c8
