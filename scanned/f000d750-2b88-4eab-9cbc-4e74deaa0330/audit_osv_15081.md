# [M] CVE-2019-13296

## Summary
Severity: Medium
Advisory: CVE-2019-13296
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/CVE-2019-13296
Type: osv

## Details
ImageMagick 7.0.8-50 Q16 has direct memory leaks in AcquireMagickMemory because of an error in CLIListOperatorImages in MagickWand/operation.c for a NULL value.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- https://github.com/ImageMagick/ImageMagick/commit/ce08a3691a8ac29125e29fc41967b3737fa3f425
- https://github.com/ImageMagick/ImageMagick/issues/1604
