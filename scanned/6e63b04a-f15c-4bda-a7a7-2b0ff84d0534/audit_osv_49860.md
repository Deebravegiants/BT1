# [M] CVE-2019-20005

## Summary
Severity: Medium
Advisory: CVE-2019-20005
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-26
Source: https://osv.dev/vulnerability/CVE-2019-20005
Type: osv

## Details
An issue was discovered in ezXML 0.8.3 through 0.8.6. The function ezxml_decode, while parsing a crafted XML file, performs incorrect memory handling, leading to a heap-based buffer over-read while running strchr() starting with a pointer after a '\0' character (where the processing of a string was finished).

## References
- https://sourceforge.net/p/ezxml/bugs/14/
