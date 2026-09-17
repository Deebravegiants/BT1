# [H] CVE-2019-8377

## Summary
Severity: High
Advisory: CVE-2019-8377
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-17
Source: https://osv.dev/vulnerability/CVE-2019-8377
Type: osv

## Details
An issue was discovered in Tcpreplay 4.3.1. A NULL pointer dereference occurred in the function get_ipv6_l4proto() located at get.c. This can be triggered by sending a crafted pcap file to the tcpreplay-edit binary. It allows an attacker to cause a Denial of Service (Segmentation fault) or possibly have unspecified other impact.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4V3SADKXUSHWTVAPU3WLXBDEQUHRA6ZO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4YAT4AGTHQKB74ETOQPJMV67TSDIAPOC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EB3ASS7URTIA3IFSBL2DIWJAFKTBJCAW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MLPY6W7Z7G6PF2JN4LXXHCACYLD4RBG6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UOSEIQ3D2OONCJEVMGC2TYBC2QX4E5EJ/
- http://www.securityfocus.com/bid/107085
- https://github.com/appneta/tcpreplay/issues/536
- https://research.loginsoft.com/bugs/null-pointer-dereference-vulnerability-in-function-get_ipv6_l4proto-tcpreplay-4-3-1/
