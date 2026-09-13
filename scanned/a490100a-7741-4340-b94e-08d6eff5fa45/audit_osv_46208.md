# [M] JLSEC-2026-814

## Summary
Severity: Medium
Advisory: JLSEC-2026-814
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-814
Type: osv

## Affected
- Julia: `Giflib_jll` — affected >=0 <5.2.1+0

## Details
In GIFLIB before 2019-02-16, a malformed GIF file triggers a divide-by-zero exception in the decoder function DGifSlurp in `dgif_lib.c` if the height field of the ImageSize data structure is equal to zero.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=13008
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=13008
- https://lists.debian.org/debian-lts-announce/2022/12/msg00008.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00008.html
- https://usn.ubuntu.com/4107-1/
- https://usn.ubuntu.com/4107-1/
