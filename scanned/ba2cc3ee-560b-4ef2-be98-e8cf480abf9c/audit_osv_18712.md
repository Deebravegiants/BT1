# [M] CVE-2020-35533

## Summary
Severity: Medium
Advisory: CVE-2020-35533
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2020-35533
Type: osv

## Details
In LibRaw, an out-of-bounds read vulnerability exists within the "LibRaw::adobe_copy_pixel()" function (libraw\src\decoders\dng.cpp) when reading data from the image file.

## References
- https://lists.debian.org/debian-lts-announce/2022/09/msg00024.html
- https://github.com/LibRaw/LibRaw/commit/a6937d4046a7c4742b683a04c8564605fd9be4fb
- https://github.com/LibRaw/LibRaw/issues/273
