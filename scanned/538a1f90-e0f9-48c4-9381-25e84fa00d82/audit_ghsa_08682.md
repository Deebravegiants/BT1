# [M] Apache Shiro sends sensitive cookies in HTTPS session without 'Secure' attribute

## Summary
Severity: Medium
Advisory: GHSA-c6r4-qjmw-cvj2
CVE: CVE-2026-43828
CWE: CWE-614
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N/RE:L/U:Amber (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-c6r4-qjmw-cvj2
Type: github-advisory

## Affected
- Maven: `org.apache.shiro:shiro-web` — affected >=1.0.0-incubating <2.2.0
- Maven: `org.apache.shiro:shiro-web` — affected >=3.0.0-alpha-1 <3.0.0-alpha-2

## Details
Default configurations of Apache Shiro send sensitive cookies in HTTPS session without 'Secure' attribute.

This issue affects Apache Shiro from 1.0 to 2.1.0, and 3.0.0-alpha-1.

Users are recommended to upgrade to version 2.1.1, or 3.0.0-alpha-2 or later, which fixes the issue.

In the affected versions, Shiro-native session manager, as well as Remember-Me manager sends JSESSIONID and rememberMe cookies without 'secure' attribute by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43828
- https://github.com/apache/shiro
- https://shiro.apache.org/security-reports.html#cve_2026_43828
- http://www.openwall.com/lists/oss-security/2026/05/25/7
