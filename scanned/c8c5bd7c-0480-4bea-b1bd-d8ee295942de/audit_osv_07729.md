# [C] Apache Tomcat: Logged effective web.xml is incomplete

## Summary
Severity: Critical
Advisory: BIT-tomcat-2026-55276
Aliases: CVE-2026-55276
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-55276
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.23

## Details
Always-Incorrect Control Flow Implementation vulnerability in Apache Tomcat meant that special roles and empty authorisation constraints were not included when the effective web.xml was logged.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.22, from 10.1.0 through 10.1.55, from 9.0.0 through 9.0.118, from 8.5.0 through 8.5.100. Other versions that have reached end of support may also be affected.

Users are recommended to upgrade to version 11.0.23, 10.1.56 or 9.0.119 which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/23
- https://lists.apache.org/thread/jy09xjlzn6r2qwvqoph8vcmf959yq68v
- https://nvd.nist.gov/vuln/detail/CVE-2026-55276
