# [M] CVE-2020-35535

## Summary
Severity: Medium
Advisory: CVE-2020-35535
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2020-35535
Type: osv

## Details
In LibRaw, there is an out-of-bounds read vulnerability within the "LibRaw::parseSonySRF()" function (libraw\src\metadata\sony.cpp) when processing srf files.

## References
- https://github.com/LibRaw/LibRaw/commit/c243f4539233053466c1309bde606815351bee81
- https://github.com/LibRaw/LibRaw/issues/283
