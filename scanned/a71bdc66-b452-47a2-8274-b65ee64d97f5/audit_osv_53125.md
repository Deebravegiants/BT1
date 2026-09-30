# [M] CVE-2022-30045

## Summary
Severity: Medium
Advisory: CVE-2022-30045
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-05-17
Source: https://osv.dev/vulnerability/CVE-2022-30045
Type: osv

## Details
An issue was discovered in libezxml.a in ezXML 0.8.6. The function ezxml_decode() performs incorrect memory handling while parsing crafted XML files, leading to a heap out-of-bounds read.

## References
- https://sourceforge.net/p/ezxml/bugs/29/
