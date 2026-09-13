# [M] CVE-2019-20198

## Summary
Severity: Medium
Advisory: CVE-2019-20198
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-31
Source: https://osv.dev/vulnerability/CVE-2019-20198
Type: osv

## Details
An issue was discovered in ezXML 0.8.3 through 0.8.6. The function ezxml_ent_ok() mishandles recursion, leading to stack consumption for a crafted XML file.

## References
- https://sourceforge.net/p/ezxml/bugs/20/
