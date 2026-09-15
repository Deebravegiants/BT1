# [M] CVE-2019-20201

## Summary
Severity: Medium
Advisory: CVE-2019-20201
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-31
Source: https://osv.dev/vulnerability/CVE-2019-20201
Type: osv

## Details
An issue was discovered in ezXML 0.8.3 through 0.8.6. The ezxml_parse_* functions mishandle XML entities, leading to an infinite loop in which memory allocations occur.

## References
- https://sourceforge.net/p/ezxml/bugs/16/
