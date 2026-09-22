# [M] CVE-2021-30485

## Summary
Severity: Medium
Advisory: CVE-2021-30485
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-11
Source: https://osv.dev/vulnerability/CVE-2021-30485
Type: osv

## Details
An issue was discovered in libezxml.a in ezXML 0.8.6. The function ezxml_internal_dtd(), while parsing a crafted XML file, performs incorrect memory handling, leading to a NULL pointer dereference while running strcmp() on a NULL pointer.

## References
- https://lists.debian.org/debian-lts-announce/2021/07/msg00005.html
- https://sourceforge.net/p/ezxml/bugs/25/
