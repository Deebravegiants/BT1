# [M] Apache Calcite is Vulnerable to Use of Externally-Controlled Input to Select Classes

## Summary
Severity: Medium
Advisory: GHSA-c2rv-hwqm-wjpg
CVE: CVE-2026-46718
CWE: CWE-470
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-02
Source: https://github.com/advisories/GHSA-c2rv-hwqm-wjpg
Type: github-advisory

## Affected
- Maven: `org.apache.calcite:calcite-core` — affected >=1.5.0 <1.42.0

## Details
Use of Externally-Controlled Input to Select Classes or Code ('Unsafe Reflection') vulnerability in Apache Calcite.

This issue affects Apache Calcite: from 1.5.0 before 1.42.

Users are recommended to upgrade to version 1.42, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46718
- https://github.com/apache/calcite/commit/5855cfa14d8038e2a123ff6ce9722edce0e0cc25
- https://github.com/apache/calcite
- https://issues.apache.org/jira/browse/CALCITE-7532
- https://lists.apache.org/thread/9s37svo343w5ck1ovh478lkzcqk4949v
- http://www.openwall.com/lists/oss-security/2026/06/01/7
