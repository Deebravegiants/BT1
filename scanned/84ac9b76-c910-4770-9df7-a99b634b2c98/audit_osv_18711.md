# [M] CVE-2020-35532

## Summary
Severity: Medium
Advisory: CVE-2020-35532
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2020-35532
Type: osv

## Details
In LibRaw, an out-of-bounds read vulnerability exists within the "simple_decode_row()" function (libraw\src\x3f\x3f_utils_patched.cpp) which can be triggered via an image with a large row_stride field.

## References
- https://lists.debian.org/debian-lts-announce/2022/09/msg00024.html
- https://github.com/LibRaw/LibRaw/commit/5ab45b085898e379fedc6b113e2e82a890602b1e
- https://github.com/LibRaw/LibRaw/issues/271
