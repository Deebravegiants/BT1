# [H] Erxes Incorrect Access Control vulnerability

## Summary
Severity: High
Advisory: GHSA-7rhv-xm4q-wh42
CVE: CVE-2024-57190
CWE: CWE-284, CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-7rhv-xm4q-wh42
Type: github-advisory

## Affected
- npm: `erxes` — affected >=0 <1.6.1

## Details
Erxes <1.6.1 is vulnerable to Incorrect Access Control. An attacker can bypass authentication by providing a "User" HTTP header that contains any user, allowing them to talk to any GraphQL endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57190
- https://github.com/erxes/erxes/commit/4ed2ca797241d2ba0c9083feeadd9755c1310ce8
- https://github.com/erxes/erxes
- https://www.sonarsource.com/blog/micro-services-major-headaches-detecting-vulnerabilities-in-erxes-microservices
