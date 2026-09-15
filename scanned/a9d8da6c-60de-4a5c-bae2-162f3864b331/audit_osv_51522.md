# [M] CVE-2021-31229

## Summary
Severity: Medium
Advisory: CVE-2021-31229
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-15
Source: https://osv.dev/vulnerability/CVE-2021-31229
Type: osv

## Details
An issue was discovered in libezxml.a in ezXML 0.8.6. The function ezxml_internal_dtd() performs incorrect memory handling while parsing crafted XML files, which leads to an out-of-bounds write of a one byte constant.

## References
- https://lists.debian.org/debian-lts-announce/2021/07/msg00005.html
- https://sourceforge.net/p/ezxml/bugs/26/
