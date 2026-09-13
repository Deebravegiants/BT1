# [M] CVE-2016-9825

## Summary
Severity: Medium
Advisory: CVE-2016-9825
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2016-9825
Type: osv

## Details
libswscale/utils.c in libav 11.8 allows remote attackers to cause a denial of service (crash) via vectors involving left shift of a negative value.

## References
- http://www.securityfocus.com/bid/94732
- https://blogs.gentoo.org/ago/2016/12/01/libav-multiple-crashes-from-the-undefined-behavior-sanitizer/
