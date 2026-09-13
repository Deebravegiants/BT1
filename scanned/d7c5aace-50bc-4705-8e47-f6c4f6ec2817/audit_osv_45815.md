# [M] JLSEC-2026-361

## Summary
Severity: Medium
Advisory: JLSEC-2026-361
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/JLSEC-2026-361
Type: osv

## Affected
- Julia: `LibGD_jll` — affected >=0 <2.3.3+0

## Details
The GD Graphics Library (aka LibGD) through 2.3.2 has an out-of-bounds read because of the lack of certain gdGetBuf and gdPutBuf return value checks.

## References
- https://github.com/libgd/libgd/commit/6f5136821be86e7068fcdf651ae9420b5d42e9a9
- https://github.com/libgd/libgd/issues/750#issuecomment-914872385
- https://lists.debian.org/debian-lts-announce/2024/04/msg00003.html
