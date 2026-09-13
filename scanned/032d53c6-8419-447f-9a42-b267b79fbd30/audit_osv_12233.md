# [M] CVE-2018-10958

## Summary
Severity: Medium
Advisory: CVE-2018-10958
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-10
Source: https://osv.dev/vulnerability/CVE-2018-10958
Type: osv

## Details
In types.cpp in Exiv2 0.26, a large size value may lead to a SIGABRT during an attempt at memory allocation for an Exiv2::Internal::PngChunk::zlibUncompress call.

## References
- https://access.redhat.com/errata/RHSA-2019:2101
- https://lists.debian.org/debian-lts-announce/2018/06/msg00010.html
- https://lists.debian.org/debian-lts-announce/2018/10/msg00012.html
- https://security.gentoo.org/glsa/201811-14
- https://usn.ubuntu.com/3700-1/
- https://www.debian.org/security/2018/dsa-4238
- https://github.com/Exiv2/exiv2/issues/302
