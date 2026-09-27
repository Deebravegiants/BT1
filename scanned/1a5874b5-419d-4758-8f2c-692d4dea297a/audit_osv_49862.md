# [M] CVE-2019-20007

## Summary
Severity: Medium
Advisory: CVE-2019-20007
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-26
Source: https://osv.dev/vulnerability/CVE-2019-20007
Type: osv

## Details
An issue was discovered in ezXML 0.8.2 through 0.8.6. The function ezxml_str2utf8, while parsing a crafted XML file, performs zero-length reallocation in ezxml.c, leading to returning a NULL pointer (in some compilers). After this, the function ezxml_parse_str does not check whether the s variable is not NULL in ezxml.c, leading to a NULL pointer dereference and crash (segmentation fault).

## References
- https://sourceforge.net/p/ezxml/bugs/13/
