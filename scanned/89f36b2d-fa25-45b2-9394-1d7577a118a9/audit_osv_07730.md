# [M] Apache Tomcat: EncryptInterceptor not protected against replay attacks

## Summary
Severity: Medium
Advisory: BIT-tomcat-2026-55955
Aliases: CVE-2026-55955
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-55955
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.23

## Details
Improper Authentication vulnerability in Apache Tomcat allowed a replay attack against the EncryptionInterceptor in the cluster component.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.22, from 10.1.0 through 10.1.55, from 9.0.13 through 9.0.18, from 8.5.38 through 8.5.100, from 7.0.100 through 7.0.109.

Users are recommended to upgrade to version 11.0.23, 10.1.56, 9.0.119, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/24
- https://lists.apache.org/thread/g4p5sf45p3f9r011pwqs9r54yd64s106
- https://nvd.nist.gov/vuln/detail/CVE-2026-55955
