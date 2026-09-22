# [M] CVE-2018-14679

## Summary
Severity: Medium
Advisory: CVE-2018-14679
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-28
Source: https://osv.dev/vulnerability/CVE-2018-14679
Type: osv

## Details
An issue was discovered in mspack/chmd.c in libmspack before 0.7alpha. There is an off-by-one error in the CHM PMGI/PMGL chunk number validity checks, which could lead to denial of service (uninitialized data dereference and application crash).

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
- https://bugs.debian.org/904802
- https://github.com/kyz/libmspack/commit/72e70a921f0f07fee748aec2274b30784e1d312a
