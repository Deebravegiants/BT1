# [C] CVE-2018-18408

## Summary
Severity: Critical
Advisory: CVE-2018-18408
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-17
Source: https://osv.dev/vulnerability/CVE-2018-18408
Type: osv

## Details
A use-after-free was discovered in the tcpbridge binary of Tcpreplay 4.3.0 beta1. The issue gets triggered in the function post_args() at tcpbridge.c, causing a denial of service or possibly unspecified other impact.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4V3SADKXUSHWTVAPU3WLXBDEQUHRA6ZO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MLPY6W7Z7G6PF2JN4LXXHCACYLD4RBG6/
- https://github.com/SegfaultMasters/covering360/blob/master/tcpreplay/README.md#use-after-free-in-post_args
- https://github.com/appneta/tcpreplay/issues/489
