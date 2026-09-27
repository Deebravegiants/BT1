# [M] CVE-2018-20005

## Summary
Severity: Medium
Advisory: CVE-2018-20005
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/CVE-2018-20005
Type: osv

## Details
An issue has been found in Mini-XML (aka mxml) 2.12. It is a use-after-free in mxmlWalkNext in mxml-search.c, as demonstrated by mxmldoc.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N53IJHDYR5HVQLKH4J6B27OEQLGKSGY5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RNWF6BAU7S42O4LE4B74KIMHFE2HDNMI/
- https://github.com/michaelrsweet/mxml/issues/234
- https://github.com/fouzhe/security/tree/master/mxml#heap-use-after-free-in-function-mxmlwalknext
