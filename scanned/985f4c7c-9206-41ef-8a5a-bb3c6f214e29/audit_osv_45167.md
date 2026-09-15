# [M] An issue was discovered in cairo 1.16.0

## Summary
Severity: Medium
Advisory: JLSEC-2025-15
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-15
Type: osv

## Affected
- Julia: `Cairo_jll` — affected >=1.16.0+0 <1.18.0+0

## Details
An issue was discovered in cairo 1.16.0. There is an assertion problem in the function `_cairo_arc_in_direction` in the file cairo-arc.c.

## References
- https://github.com/TeamSeri0us/pocs/tree/master/gerbv
- https://gitlab.freedesktop.org/cairo/cairo/issues/352
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
