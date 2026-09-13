# [C] CVE-2020-12740

## Summary
Severity: Critical
Advisory: CVE-2020-12740
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-05-08
Source: https://osv.dev/vulnerability/CVE-2020-12740
Type: osv

## Details
tcprewrite in Tcpreplay through 4.3.2 has a heap-based buffer over-read during a get_c operation. The issue is being triggered in the function get_ipv6_next() at common/get.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4YAT4AGTHQKB74ETOQPJMV67TSDIAPOC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UOSEIQ3D2OONCJEVMGC2TYBC2QX4E5EJ/
- https://github.com/appneta/tcpreplay/issues/576
