# [C] Apache IoTDB has an Insecure Default Configuration Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-74cf-pgh9-m5q2
CVE: CVE-2026-24015
CWE: CWE-1327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-74cf-pgh9-m5q2
Type: github-advisory

## Affected
- Maven: `org.apache.iotdb:iotdb-core` — affected >=1.0.0 <1.3.7
- Maven: `org.apache.iotdb:iotdb-core` — affected >=2.0.0 <2.0.7

## Details
A vulnerability in Apache IoTDB.

This issue affects Apache IoTDB: from 1.0.0 before 1.3.7, from 2.0.0 before 2.0.7.

Users are recommended to upgrade to version 1.3.7 or 2.0.7, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24015
- https://github.com/apache/iotdb
- https://github.com/apache/iotdb/compare/v1.3.6...v1.3.7
- https://github.com/apache/iotdb/compare/v2.0.6...v2.0.7
- https://github.com/apache/iotdb/releases/tag/v1.3.7
- https://github.com/apache/iotdb/releases/tag/v2.0.7
- https://lists.apache.org/thread/j769ywdqm46zl3oz5lbffsldklg0ow7p
- http://www.openwall.com/lists/oss-security/2026/03/09/5
