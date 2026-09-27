# [M] CVE-2017-8782

## Summary
Severity: Medium
Advisory: CVE-2017-8782
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-31
Source: https://osv.dev/vulnerability/CVE-2017-8782
Type: osv

## Details
The readString function in util/read.c and util/old/read.c in libming 0.4.8 allows remote attackers to cause a denial of service via a large file that is mishandled by listswf, listaction, etc. This occurs because of an integer overflow that leads to a memory allocation error.

## References
- http://www.securityfocus.com/bid/98793
- http://seclists.org/fulldisclosure/2017/May/106
