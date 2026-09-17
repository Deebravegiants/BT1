# [M] CVE-2018-16336

## Summary
Severity: Medium
Advisory: CVE-2018-16336
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-02
Source: https://osv.dev/vulnerability/CVE-2018-16336
Type: osv

## Details
Exiv2::Internal::PngChunk::parseTXTChunk in Exiv2 v0.26 allows remote attackers to cause a denial of service (heap-based buffer over-read) via a crafted image file, a different vulnerability than CVE-2018-10999.

## References
- https://github.com/Exiv2/exiv2/issues/400
- https://lists.debian.org/debian-lts-announce/2018/10/msg00012.html
- https://usn.ubuntu.com/3852-1/
