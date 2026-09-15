# [M] CVE-2018-18407

## Summary
Severity: Medium
Advisory: CVE-2018-18407
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-17
Source: https://osv.dev/vulnerability/CVE-2018-18407
Type: osv

## Details
A heap-based buffer over-read was discovered in the tcpreplay-edit binary of Tcpreplay 4.3.0 beta1, during the incremental checksum operation. The issue gets triggered in the function csum_replace4() in incremental_checksum.h, causing a denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4V3SADKXUSHWTVAPU3WLXBDEQUHRA6ZO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MLPY6W7Z7G6PF2JN4LXXHCACYLD4RBG6/
- https://github.com/appneta/tcpreplay/issues/488
- https://github.com/SegfaultMasters/covering360/blob/master/tcpreplay/README.md#user-content-heap-overflow-in-csum_replace4
