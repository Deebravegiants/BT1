# [H] Apache Tomcat: TOCTOU when setting specific permissions for Unix Domain Sockets

## Summary
Severity: High
Advisory: BIT-tomcat-2026-65183
Aliases: CVE-2026-65183
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-65183
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.25

## Details
Time-of-check Time-of-use (TOCTOU) Race Condition vulnerability in Apache Tomcat when creating unix domain sockets allows an unauthorised local user to access the unix domain socket.



This issue affects Apache Tomcat: from 11.0.0 through 11.0.24, from 10.1.0 through 10.1.57, from 9.0.42 through 9.0.120.



Users are recommended to upgrade to version 11.0.25, 10.1.58, 9.0.121, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/26/2
- https://lists.apache.org/thread/748o4st6d5dk6n3l7tgzo5yl68gg05c0
- https://nvd.nist.gov/vuln/detail/CVE-2026-65183
