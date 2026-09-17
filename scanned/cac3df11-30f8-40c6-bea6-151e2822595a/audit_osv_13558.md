# [H] CVE-2018-20330

## Summary
Severity: High
Advisory: CVE-2018-20330
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-21
Source: https://osv.dev/vulnerability/CVE-2018-20330
Type: osv

## Details
The tjLoadImage function in libjpeg-turbo 2.0.1 has an integer overflow with a resultant heap-based buffer overflow via a BMP image because multiplication of pitch and height is mishandled, as demonstrated by tjbench.

## References
- https://usn.ubuntu.com/4190-1/
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/304
