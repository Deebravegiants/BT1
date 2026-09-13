# [H] CVE-2020-14153

## Summary
Severity: High
Advisory: CVE-2020-14153
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2020-06-15
Source: https://osv.dev/vulnerability/CVE-2020-14153
Type: osv

## Details
In IJG JPEG (aka libjpeg) from version 8 through 9c, jdhuff.c has an out-of-bounds array read for certain table pointers.

## References
- http://www.ijg.org/files/jpegsrc.v9d.tar.gz
- https://bugs.gentoo.org/727908
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/445
