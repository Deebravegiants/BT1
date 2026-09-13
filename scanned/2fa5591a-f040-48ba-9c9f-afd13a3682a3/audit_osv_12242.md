# [M] CVE-2018-10999

## Summary
Severity: Medium
Advisory: CVE-2018-10999
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-12
Source: https://osv.dev/vulnerability/CVE-2018-10999
Type: osv

## Details
An issue was discovered in Exiv2 0.26. The Exiv2::Internal::PngChunk::parseTXTChunk function has a heap-based buffer over-read.

## References
- https://lists.debian.org/debian-lts-announce/2018/06/msg00010.html
- https://lists.debian.org/debian-lts-announce/2018/10/msg00012.html
- https://security.gentoo.org/glsa/201811-14
- https://usn.ubuntu.com/3700-1/
- https://www.debian.org/security/2018/dsa-4238
- https://github.com/Exiv2/exiv2/issues/306
