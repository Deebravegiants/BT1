# [H] CVE-2019-8381

## Summary
Severity: High
Advisory: CVE-2019-8381
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-17
Source: https://osv.dev/vulnerability/CVE-2019-8381
Type: osv

## Details
An issue was discovered in Tcpreplay 4.3.1. An invalid memory access occurs in do_checksum in checksum.c. It can be triggered by sending a crafted pcap file to the tcpreplay-edit binary. It allows an attacker to cause a Denial of Service (Segmentation fault) or possibly have unspecified other impact.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4V3SADKXUSHWTVAPU3WLXBDEQUHRA6ZO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EB3ASS7URTIA3IFSBL2DIWJAFKTBJCAW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MLPY6W7Z7G6PF2JN4LXXHCACYLD4RBG6/
- https://github.com/appneta/tcpreplay/issues/538
- https://research.loginsoft.com/bugs/invalid-memory-access-vulnerability-in-function-do_checksum-tcpreplay-4-3-1/
