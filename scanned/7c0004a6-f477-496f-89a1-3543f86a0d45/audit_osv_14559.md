# [M] CVE-2019-1010305

## Summary
Severity: Medium
Advisory: CVE-2019-1010305
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-07-15
Source: https://osv.dev/vulnerability/CVE-2019-1010305
Type: osv

## Details
libmspack 0.9.1alpha is affected by: Buffer Overflow. The impact is: Information Disclosure. The component is: function chmd_read_headers() in libmspack(file libmspack/mspack/chmd.c). The attack vector is: the victim must open a specially crafted chm file. The fixed version is: after commit 2f084136cfe0d05e5bf5703f3e83c6d955234b4d.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IXWNEY4CJBLPRKV6LG7FQUPD6WVZYBTB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S2QJTUAGP22YY7453MHGTFN4YQE5HJBR/
- https://lists.debian.org/debian-lts-announce/2019/08/msg00028.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00033.html
- https://usn.ubuntu.com/4066-1/
- https://usn.ubuntu.com/4066-2/
- https://github.com/kyz/libmspack/issues/27
- https://github.com/kyz/libmspack/commit/2f084136cfe0d05e5bf5703f3e83c6d955234b4d
