# [H] The tjLoadImage function in libjpeg-turbo 2.0.1 has an integer overflow with a resultant heap-based...

## Summary
Severity: High
Advisory: JLSEC-2025-178
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-21
Source: https://osv.dev/vulnerability/JLSEC-2025-178
Type: osv

## Affected
- Julia: `JpegTurbo_jll` — affected >=0 <2.1.0+0

## Details
The tjLoadImage function in libjpeg-turbo 2.0.1 has an integer overflow with a resultant heap-based buffer overflow via a BMP image because multiplication of pitch and height is mishandled, as demonstrated by tjbench.

## References
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/304
- https://usn.ubuntu.com/4190-1/
