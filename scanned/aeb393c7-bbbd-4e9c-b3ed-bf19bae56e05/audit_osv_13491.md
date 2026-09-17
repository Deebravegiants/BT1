# [H] CVE-2018-20004

## Summary
Severity: High
Advisory: CVE-2018-20004
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/CVE-2018-20004
Type: osv

## Details
An issue has been found in Mini-XML (aka mxml) 2.12. It is a stack-based buffer overflow in mxml_write_node in mxml-file.c via vectors involving a double-precision floating point number and the '<order type="real">' substring, as demonstrated by testmxml.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N53IJHDYR5HVQLKH4J6B27OEQLGKSGY5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RNWF6BAU7S42O4LE4B74KIMHFE2HDNMI/
- https://lists.debian.org/debian-lts-announce/2019/01/msg00018.html
- https://github.com/fouzhe/security/tree/master/mxml#stack-buffer-overflow-in-function-mxml_write_node
- https://github.com/michaelrsweet/mxml/issues/233
