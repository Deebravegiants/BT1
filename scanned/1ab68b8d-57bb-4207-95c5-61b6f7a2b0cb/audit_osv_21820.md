# [M] CVE-2021-46822

## Summary
Severity: Medium
Advisory: CVE-2021-46822
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-06-18
Source: https://osv.dev/vulnerability/CVE-2021-46822
Type: osv

## Details
The PPM reader in libjpeg-turbo through 2.0.90 mishandles use of tjLoadImage for loading a 16-bit binary PPM file into a grayscale buffer and loading a 16-bit binary PGM file into an RGB buffer. This is related to a heap-based buffer overflow in the get_word_rgb_row function in rdppm.c.

## References
- https://exchange.xforce.ibmcloud.com/vulnerabilities/221567
- https://github.com/libjpeg-turbo/libjpeg-turbo/commit/f35fd27ec641c42d6b115bfa595e483ec58188d2
