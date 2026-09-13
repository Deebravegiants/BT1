# [C] CVE-2017-14062

## Summary
Severity: Critical
Advisory: CVE-2017-14062
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-31
Source: https://osv.dev/vulnerability/CVE-2017-14062
Type: osv

## Details
Integer overflow in the decode_digit function in puny_decode.c in Libidn2 before 2.0.4 allows remote attackers to cause a denial of service or possibly have unspecified other impact.

## References
- http://www.debian.org/security/2017/dsa-3988
- https://gitlab.com/libidn/libidn2/blob/master/NEWS
- https://lists.debian.org/debian-lts-announce/2018/07/msg00040.html
- https://gitlab.com/libidn/libidn2/commit/3284eb342cd0ed1a18786e3fcdf0cdd7e76676bd
