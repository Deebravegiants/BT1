# [M] CVE-2017-17669

## Summary
Severity: Medium
Advisory: CVE-2017-17669
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-13
Source: https://osv.dev/vulnerability/CVE-2017-17669
Type: osv

## Details
There is a heap-based buffer over-read in the Exiv2::Internal::PngChunk::keyTXTChunk function of pngchunk_int.cpp in Exiv2 0.26. A crafted PNG file will lead to a remote denial of service attack.

## References
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://usn.ubuntu.com/3852-1/
- https://github.com/Exiv2/exiv2/issues/187
