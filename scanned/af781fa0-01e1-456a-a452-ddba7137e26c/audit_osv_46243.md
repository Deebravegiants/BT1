# [M] JLSEC-2026-875

## Summary
Severity: Medium
Advisory: JLSEC-2026-875
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-875
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.0+0

## Details
A heap based buffer overflow in `coders/tiff.c` may result in program crash and denial of service in ImageMagick before 7.0.10-45.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1922525
- https://bugzilla.redhat.com/show_bug.cgi?id=1922525
- https://github.com/ImageMagick/ImageMagick/commit/6ee5059cd3ac8d82714a1ab1321399b88539abf0
- https://github.com/ImageMagick/ImageMagick/commit/6ee5059cd3ac8d82714a1ab1321399b88539abf0
