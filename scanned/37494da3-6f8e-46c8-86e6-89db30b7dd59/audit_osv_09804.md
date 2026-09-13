# [M] CVE-2017-11537

## Summary
Severity: Medium
Advisory: CVE-2017-11537
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11537
Type: osv

## Details
When ImageMagick 7.0.6-1 processes a crafted file in convert, it can lead to a Floating Point Exception (FPE) in the WritePALMImage() function in coders/palm.c, related to an incorrect bits-per-pixel calculation.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2017/dsa-4019
- https://github.com/ImageMagick/ImageMagick/issues/560
