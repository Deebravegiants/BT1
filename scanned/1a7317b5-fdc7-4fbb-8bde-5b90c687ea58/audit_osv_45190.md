# [M] libjpeg-turbo 2.0.1 has a heap-based buffer over-read in the `put_pixel_rows` function in wrbmp.c,...

## Summary
Severity: Medium
Advisory: JLSEC-2025-177
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-21
Source: https://osv.dev/vulnerability/JLSEC-2025-177
Type: osv

## Affected
- Julia: `JpegTurbo_jll` — affected >=0 <2.1.0+0

## Details
libjpeg-turbo 2.0.1 has a heap-based buffer over-read in the `put_pixel_rows` function in wrbmp.c, as demonstrated by djpeg.

## References
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/305
- https://usn.ubuntu.com/4190-1/
