# [M] Apache Syncope Vulnerable to Exposure of Sensitive Information Through Data Queries

## Summary
Severity: Medium
Advisory: GHSA-vr35-jm2f-8wg2
CVE: CVE-2026-42797
CWE: CWE-202
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-vr35-jm2f-8wg2
Type: github-advisory

## Affected
- Maven: `org.apache.syncope.core:syncope-core-provisioning-api` — affected >=3.0.0-M0
- Maven: `org.apache.syncope.core:syncope-core-provisioning-api` — affected >=4.0.0-M0 <4.0.6
- Maven: `org.apache.syncope.core:syncope-core-provisioning-api` — affected >=4.1.0-M0 <4.1.1

## Details
Exposure of Sensitive Information Through Data Queries vulnerability in Apache Syncope.

An administrator with adequate entitlements for Derived Schemas can create a malicious JEXL expression which allows any administrator with sufficient entitlements for User read to access User-related security-sensitive information.

This issue affects Apache Syncope: 3.0 through 3.0.16, 4.0 through 4.0.5, 4.1.0.

Users are recommended to upgrade to version 4.0.6 / 4.1.1, which fix this issue by further restricting the JEXL expression definition.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42797
- https://github.com/apache/syncope
- https://lists.apache.org/thread/5y7d277sntyytrmxnx2tfjr9ftcpq1s6
- http://www.openwall.com/lists/oss-security/2026/05/25/5
