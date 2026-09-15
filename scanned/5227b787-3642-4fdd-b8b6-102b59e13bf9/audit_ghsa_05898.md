# [C] Apache Ranger has a Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-6qc3-v8fv-fv9j
CVE: CVE-2026-28672
CWE: CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-10
Source: https://github.com/advisories/GHSA-6qc3-v8fv-fv9j
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger` — affected >=0.6.0

## Details
Improper Neutralization of Special Elements used in a Command ('Command Injection') vulnerability in Apache Ranger.

This issue affects Apache Ranger: from 0.6 through 2.8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-28672
- https://github.com/apache/ranger
- https://lists.apache.org/thread/99ysjqcmz950o3jgm6pqx1wb696onzq7
- http://www.openwall.com/lists/oss-security/2026/08/09/2
