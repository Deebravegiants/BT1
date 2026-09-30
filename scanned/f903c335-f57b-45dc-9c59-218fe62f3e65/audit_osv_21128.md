# [M] CVE-2021-40812

## Summary
Severity: Medium
Advisory: CVE-2021-40812
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-08
Source: https://osv.dev/vulnerability/CVE-2021-40812
Type: osv

## Details
The GD Graphics Library (aka LibGD) through 2.3.2 has an out-of-bounds read because of the lack of certain gdGetBuf and gdPutBuf return value checks.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00003.html
- https://github.com/libgd/libgd/commit/6f5136821be86e7068fcdf651ae9420b5d42e9a9
- https://github.com/libgd/libgd/issues/750#issuecomment-914872385
