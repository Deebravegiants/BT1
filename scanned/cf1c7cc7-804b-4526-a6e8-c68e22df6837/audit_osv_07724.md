# [M] Apache Tomcat: Fix for CVE-2025-66614 is incomplete

## Summary
Severity: Medium
Advisory: BIT-tomcat-2026-32990
Aliases: CVE-2026-32990, GHSA-8mc5-53m5-3qj2
Ecosystem: Bitnami
Published: 2026-04-13
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-32990
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.15 <11.0.20

## Details
Improper Input Validation vulnerability in Apache Tomcat due to an incomplete fix of CVE-2025-66614.

This issue affects Apache Tomcat: from 11.0.15 through 11.0.19, from 10.1.50 through 10.1.52, from 9.0.113 through 9.0.115.

Users are recommended to upgrade to version 11.0.20, 10.1.53 or 9.0.116, which fix the issue.

## References
- https://lists.apache.org/thread/1nl9zqft0ksqlhlkd3j4obyjz1ghoyn7
- https://nvd.nist.gov/vuln/detail/CVE-2026-32990
