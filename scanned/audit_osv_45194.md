# [M] The PPM reader in libjpeg-turbo through 2.0.90 mishandles use of tjLoadImage for loading a 16-bit...

## Summary
Severity: Medium
Advisory: JLSEC-2025-180
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-21
Source: https://osv.dev/vulnerability/JLSEC-2025-180
Type: osv

## Affected
- Julia: `JpegTurbo_jll` — affected >=0 <2.1.0+0

## Details
The PPM reader in libjpeg-turbo through 2.0.90 mishandles use of tjLoadImage for loading a 16-bit binary PPM file into a grayscale buffer and loading a 16-bit binary PGM file into an RGB buffer. This is related to a heap-based buffer overflow in the `get_word_rgb_row` function in rdppm.c.

## References
- https://exchange.xforce.ibmcloud.com/vulnerabilities/221567
- https://github.com/libjpeg-turbo/libjpeg-turbo/commit/f35fd27ec641c42d6b115bfa595e483ec58188d2
