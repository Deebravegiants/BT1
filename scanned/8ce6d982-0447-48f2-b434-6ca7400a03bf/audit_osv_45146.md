# [M] cairo through 1.15.14 has an out-of-bounds stack-memory write during processing of a crafted...

## Summary
Severity: Medium
Advisory: JLSEC-2025-13
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-13
Type: osv

## Affected
- Julia: `Cairo_jll` — affected >=0 <1.16.0+0

## Details
cairo through 1.15.14 has an out-of-bounds stack-memory write during processing of a crafted document by WebKitGTK+ because of the interaction between cairo-rectangular-scan-converter.c (the generate and `render_rows` functions) and cairo-image-compositor.c (the `_cairo_image_spans_and_zero` function).

## References
- https://gitlab.freedesktop.org/cairo/cairo/issues/341
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
