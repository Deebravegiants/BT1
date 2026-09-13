# [M] CVE-2018-19664

## Summary
Severity: Medium
Advisory: CVE-2018-19664
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-19664
Type: osv

## Details
libjpeg-turbo 2.0.1 has a heap-based buffer over-read in the put_pixel_rows function in wrbmp.c, as demonstrated by djpeg.

## References
- https://usn.ubuntu.com/4190-1/
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/305
