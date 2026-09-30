# [M] Apache Tomcat: OCSP checks sometimes soft-fail with FFM even when soft-fail is disabled

## Summary
Severity: Medium
Advisory: BIT-tomcat-2026-34500
Aliases: CVE-2026-34500, GHSA-24j9-x2wg-9qv6
Ecosystem: Bitnami
Published: 2026-04-13
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-34500
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.21

## Details
CLIENT_CERT authentication does not fail as expected for some scenarios when soft fail is disabled and FFM is used in Apache Tomcat.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.20, from 10.1.22 through 10.1.53, from 9.0.92 through 9.0.116.

Users are recommended to upgrade to version 11.0.21, 10.1.54 or 9.0.117, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/04/09/29
- https://lists.apache.org/thread/7rcl4zdxryc8hy3htyfyxkbqpxjtfdl2
- https://nvd.nist.gov/vuln/detail/CVE-2026-34500
