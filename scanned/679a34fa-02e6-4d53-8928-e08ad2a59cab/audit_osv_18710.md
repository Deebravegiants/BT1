# [M] CVE-2020-35531

## Summary
Severity: Medium
Advisory: CVE-2020-35531
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2020-35531
Type: osv

## Details
In LibRaw, an out-of-bounds read vulnerability exists within the get_huffman_diff() function (libraw\src\x3f\x3f_utils_patched.cpp) when reading data from an image file.

## References
- https://lists.debian.org/debian-lts-announce/2022/09/msg00024.html
- https://github.com/LibRaw/LibRaw/commit/d75af00681a74dcc8b929207eb895611a6eceb68
- https://github.com/LibRaw/LibRaw/issues/270
