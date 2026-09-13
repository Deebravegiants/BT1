# [C] Apache Ranger UI vulnerable to Server Side Request Forgery

## Summary
Severity: Critical
Advisory: GHSA-g9gf-g5jq-9h3v
CVE: CVE-2024-45479
CWE: CWE-20, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-01-22
Source: https://github.com/advisories/GHSA-g9gf-g5jq-9h3v
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger` — affected >=0.5.0 <2.5.0

## Details
SSRF vulnerability in Edit Service Page of Apache Ranger UI in Apache Ranger Version 2.4.0.
Users are recommended to upgrade to version Apache Ranger 2.5.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45479
- https://github.com/apache/ranger/commit/447658578decf33d2b68d872a32db59227dfef1b#diff-0cb27d5067c1eced82c6a8a755e6142d20c633820996701a1ca616345ea8b1ca
- https://cwiki.apache.org/confluence/display/RANGER/Vulnerabilities+found+in+Ranger
- https://github.com/apache/ranger
- http://www.openwall.com/lists/oss-security/2025/01/21/4
