# [H] CVE-2021-31598

## Summary
Severity: High
Advisory: CVE-2021-31598
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-24
Source: https://osv.dev/vulnerability/CVE-2021-31598
Type: osv

## Details
An issue was discovered in libezxml.a in ezXML 0.8.6. The function ezxml_decode() performs incorrect memory handling while parsing crafted XML files, leading to a heap-based buffer overflow.

## References
- https://lists.debian.org/debian-lts-announce/2021/07/msg00005.html
- https://sourceforge.net/p/ezxml/bugs/28/
