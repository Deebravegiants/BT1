# [C] CVE-2005-1141

## Summary
Severity: Critical
Advisory: CVE-2005-1141
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2005-04-15
Source: https://osv.dev/vulnerability/CVE-2005-1141
Type: osv

## Details
Integer overflow in the readpgm function in pnm.c for GOCR 0.40, when using the netpbm library, allows remote attackers to execute arbitrary code via a PNM file with large width and height values, which leads to a heap-based buffer overflow.

## References
- http://www.overflow.pl/adv/gocr.txt
- http://marc.info/?l=bugtraq&m=111358557823673&w=2
- http://marc.info/?l=bugtraq&m=111358557823673&w=2
- http://www.overflow.pl/adv/gocr.txt
- http://www.overflow.pl/adv/gocr.txt
