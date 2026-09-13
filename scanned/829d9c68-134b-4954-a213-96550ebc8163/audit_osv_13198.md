# [M] CVE-2018-18585

## Summary
Severity: Medium
Advisory: CVE-2018-18585
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2018-10-23
Source: https://osv.dev/vulnerability/CVE-2018-18585
Type: osv

## Details
chmd_read_headers in mspack/chmd.c in libmspack before 0.8alpha accepts a filename that has '\0' as its first or second character (such as the "/\0" name).

## References
- https://access.redhat.com/errata/RHSA-2019:2049
- https://lists.debian.org/debian-lts-announce/2018/10/msg00017.html
- https://security.gentoo.org/glsa/201903-20
- https://usn.ubuntu.com/3814-1/
- https://usn.ubuntu.com/3814-2/
- https://usn.ubuntu.com/3814-3/
- https://www.starwindsoftware.com/security/sw-20181213-0002/
- https://bugs.debian.org/911637
- https://www.openwall.com/lists/oss-security/2018/10/22/1
- https://github.com/kyz/libmspack/commit/8759da8db6ec9e866cb8eb143313f397f925bb4f
