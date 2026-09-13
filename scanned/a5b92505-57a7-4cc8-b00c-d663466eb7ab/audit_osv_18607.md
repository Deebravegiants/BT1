# [M] CVE-2020-28928

## Summary
Severity: Medium
Advisory: CVE-2020-28928
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-24
Source: https://osv.dev/vulnerability/CVE-2020-28928
Type: osv

## Details
In musl libc through 1.2.1, wcsnrtombs mishandles particular combinations of destination buffer size and source character limit, as demonstrated by an invalid write access (buffer overflow).

## References
- https://lists.apache.org/thread.html/r2134abfe847bea7795f0e53756d10a47e6643f35ab8169df8b8a9eb1%40%3Cnotifications.apisix.apache.org%3E
- https://lists.apache.org/thread.html/r90b60cf49348e515257b4950900c1bd3ab95a960cf2469d919c7264e%40%3Cnotifications.apisix.apache.org%3E
- https://lists.apache.org/thread.html/ra63e8dc5137d952afc55dbbfa63be83304ecf842d1eab1ff3ebb29e2%40%3Cnotifications.apisix.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LKQ3RVSMVZNZNO4D65W2CZZ4DMYFZN2Q/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UW27QVY7ERPTSGKS4KAWE5TU7EJWHKVQ/
- http://www.openwall.com/lists/oss-security/2020/11/20/4
- https://lists.debian.org/debian-lts-announce/2020/11/msg00050.html
- https://musl.libc.org/releases.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
