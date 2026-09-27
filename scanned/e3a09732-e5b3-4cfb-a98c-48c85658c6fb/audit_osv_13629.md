# [M] CVE-2018-20592

## Summary
Severity: Medium
Advisory: CVE-2018-20592
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-30
Source: https://osv.dev/vulnerability/CVE-2018-20592
Type: osv

## Details
In Mini-XML (aka mxml) v2.12, there is a use-after-free in the mxmlAdd function of the mxml-node.c file. Remote attackers could leverage this vulnerability to cause a denial-of-service via a crafted xml file, as demonstrated by mxmldoc.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N53IJHDYR5HVQLKH4J6B27OEQLGKSGY5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RNWF6BAU7S42O4LE4B74KIMHFE2HDNMI/
- https://github.com/michaelrsweet/mxml/issues/237
- https://github.com/ntu-sec/pocs/blob/master/mxml-53c75b0/crashes/uaf_mxml-node.c:128_1.txt.err
- https://github.com/ntu-sec/pocs/blob/master/mxml-53c75b0/crashes/uaf_mxml-node.c:128_2.txt.err
