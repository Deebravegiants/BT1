# [M] JLSEC-2026-1104

## Summary
Severity: Medium
Advisory: JLSEC-2026-1104
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1104
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0 <0.22.1+0

## Details
In LibRaw, an out-of-bounds read vulnerability exists within the "`simple_decode_row()`" function (`libraw\src\x3f\x3f_utils_patched.cpp`) which can be triggered via an image with a large `row_stride` field.

## References
- https://github.com/LibRaw/LibRaw/commit/5ab45b085898e379fedc6b113e2e82a890602b1e
- https://github.com/LibRaw/LibRaw/commit/5ab45b085898e379fedc6b113e2e82a890602b1e
- https://github.com/LibRaw/LibRaw/issues/271
- https://github.com/LibRaw/LibRaw/issues/271
- https://lists.debian.org/debian-lts-announce/2022/09/msg00024.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00024.html
