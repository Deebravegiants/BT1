# [H] CVE-2017-12839

## Summary
Severity: High
Advisory: CVE-2017-12839
CVSS: 8.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2019-05-09
Source: https://osv.dev/vulnerability/CVE-2017-12839
Type: osv

## Details
A heap-based buffer over-read in the getbits function in src/libmpg123/getbits.h in mpg123 through 1.25.5 allows remote attackers to cause a possible denial-of-service (out-of-bounds read) or possibly have unspecified other impact via a crafted mp3 file.

## References
- https://www.mpg123.de/
- https://www.mpg123.de/cgi-bin/scm/mpg123/trunk/src/libmpg123/getbits.h?r1=2024&r2=4323&sortby=date
- https://sourceforge.net/p/mpg123/bugs/255/
