# [H] CVE-2018-14682

## Summary
Severity: High
Advisory: CVE-2018-14682
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-28
Source: https://osv.dev/vulnerability/CVE-2018-14682
Type: osv

## Details
An issue was discovered in mspack/chmd.c in libmspack before 0.7alpha. There is an off-by-one error in the TOLOWER() macro for CHM decompression.

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
- https://bugs.debian.org/904800
- https://github.com/kyz/libmspack/commit/4fd9ccaa54e1aebde1e4b95fb0163b699fd7bcc8
