# [H] CVE-2017-15019

## Summary
Severity: High
Advisory: CVE-2017-15019
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-15019
Type: osv

## Details
LAME 3.99.5 has a NULL Pointer Dereference in the hip_decode_init function within libmp3lame/mpglib_interface.c via a malformed mpg file, because of an incorrect calloc call.

## References
- https://sourceforge.net/p/lame/bugs/477/
