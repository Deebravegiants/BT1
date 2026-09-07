# [M] Apache Ranger Vulnerable to Improper Validation of Certificate with Host Mismatch

## Summary
Severity: Medium
Advisory: GHSA-5fvg-qwcp-r325
CVE: CVE-2025-59060
CWE: CWE-297
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-5fvg-qwcp-r325
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger-nifi-registry-plugin` — affected >=0 <2.8.0

## Details
Hostname verification bypass issue in Apache Ranger NiFiRegistryClient/NiFiClient is reported in Apache Ranger versions <= 2.7.0.

Users are recommended to upgrade to version 2.8.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59060
- https://github.com/apache/ranger
- https://lists.apache.org/thread/c4plx81z3xs86vgl3fd95y3q7hhtff05
- http://www.openwall.com/lists/oss-security/2026/03/02/4
