# [M] Apache Shiro has a session fixation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fcvm-3cpj-f9qx
CVE: CVE-2026-43827
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N/RE:L/U:Amber (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-fcvm-3cpj-f9qx
Type: github-advisory

## Affected
- Maven: `org.apache.shiro:shiro-core` — affected >=1.0.0-incubating <2.2.0
- Maven: `org.apache.shiro:shiro-core` — affected >=3.0.0-alpha-1 <3.0.0-alpha-2

## Details
Default configurations of Apache Shiro have a session fixation vulnerability.

This issue affects Apache Shiro from 1.0 to 2.1.0, and 3.0.0-alpha-1.

Users are recommended to upgrade to version 2.1.1, or 3.0.0-alpha-2 or later, which fixes the issue.

In the affected versions, when a session already exists, it is not invalidated upon successful login, nor is a new session being generated with a new ID.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43827
- https://github.com/apache/shiro
- https://shiro.apache.org/security-reports.html#cve_2026_43827
- http://www.openwall.com/lists/oss-security/2026/05/25/6
