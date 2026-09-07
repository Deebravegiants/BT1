# [M] Apache Shiro Vulnerable to Open Redirect, Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-wpqm-4gwx-w843
CVE: CVE-2026-44598
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N/S:N/AU:Y/R:A/V:D/RE:L/U:Green (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-wpqm-4gwx-w843
Type: github-advisory

## Affected
- Maven: `org.apache.shiro:shiro-jakarta-ee` — affected >=2.0.0-alpha-0 <2.2.0
- Maven: `org.apache.shiro:shiro-jakarta-ee` — affected >=3.0.0-alpha-1 <3.0.0-alpha-2

## Details
With valid login credentials, URL Redirection to Untrusted Site ('Open Redirect'), Server-Side Request Forgery (SSRF) vulnerability in Apache Shiro.

This issue affects Apache Shiro from 2.0-alpha to 2.1.0, and 3.0.0-alpha-1, only when using shiro-jakarta-ee integration module.

Users are recommended to upgrade to version 2.1.1, or 3.0.0-alpha-2 or later, which fixes the issue by encrypting the cookie.

After successful login, Jakarta EE integration module uses shiroSavedRequest cookie to redirect to a particular web page after login.
This cookie was not validated, and can be forged to send a HTTP GET request from the server itself to an arbitrary URL from the cookie.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-44598
- https://github.com/apache/shiro
- https://shiro.apache.org/security-reports.html#cve_2026_44598
- http://www.openwall.com/lists/oss-security/2026/05/25/8
