# [C] Improper Authorization in Apache Shiro

## Summary
Severity: Critical
Advisory: GHSA-4cf5-xmhp-3xj7
CVE: CVE-2022-32532
CWE: CWE-285, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-30
Source: https://github.com/advisories/GHSA-4cf5-xmhp-3xj7
Type: github-advisory

## Affected
- Maven: `org.apache.shiro:shiro-core` — affected >=0 <1.9.1

## Details
Apache Shiro before 1.9.1, A RegexRequestMatcher can be misconfigured to be bypassed on some servlet containers. Applications using RegExPatternMatcher with `.` in the regular expression are possibly vulnerable to an authorization bypass.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32532
- https://github.com/apache/shiro
- https://lists.apache.org/thread/y8260dw8vbm99oq7zv6y3mzn5ovk90xh
