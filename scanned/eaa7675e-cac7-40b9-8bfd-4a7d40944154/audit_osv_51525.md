# [M] CVE-2021-31347

## Summary
Severity: Medium
Advisory: CVE-2021-31347
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-16
Source: https://osv.dev/vulnerability/CVE-2021-31347
Type: osv

## Details
An issue was discovered in libezxml.a in ezXML 0.8.6. The function ezxml_parse_str() performs incorrect memory handling while parsing crafted XML files (writing outside a memory region created by mmap).

## References
- https://lists.debian.org/debian-lts-announce/2021/07/msg00005.html
- https://sourceforge.net/p/ezxml/bugs/27/
