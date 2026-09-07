# [C] HtmlUnit Code Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-3xrr-7m6p-p7xh
CVE: CVE-2023-26119
CWE: CWE-74, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-3xrr-7m6p-p7xh
Type: github-advisory

## Affected
- Maven: `net.sourceforge.htmlunit:htmlunit` — affected >=0 <3.0.0

## Details
Versions of the package `net.sourceforge.htmlunit:htmlunit` from 0 and before 3.0.0 are vulnerable to Remote Code Execution (RCE) via XSTL, when browsing the attacker’s webpage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26119
- https://github.com/HtmlUnit/htmlunit/commit/641325bbc84702dc9800ec7037aec061ce21956b
- https://github.com/HtmlUnit/htmlunit
- https://security.snyk.io/vuln/SNYK-JAVA-NETSOURCEFORGEHTMLUNIT-3252500
- https://siebene.github.io/2022/12/30/HtmlUnit-RCE
