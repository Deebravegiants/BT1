# [H] Unrestricted recursion in htmlunit

## Summary
Severity: High
Advisory: GHSA-rc44-5cmh-879m
CVE: CVE-2023-2798
CWE: CWE-400, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-25
Source: https://github.com/advisories/GHSA-rc44-5cmh-879m
Type: github-advisory

## Affected
- Maven: `org.htmlunit:htmlunit` — affected >=0 <2.70.0

## Details
Those using HtmlUnit to browse untrusted webpages may be vulnerable to Denial of service attacks (DoS). If HtmlUnit is running on user supplied web pages, an attacker may supply content that causes HtmlUnit to crash by a stack overflow. This effect may support a denial of service attack. This issue affects HtmlUnit before 2.70.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2798
- https://github.com/HtmlUnit/htmlunit/commit/940dc7fd
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=54613
- https://github.com/HtmlUnit/htmlunit
- https://github.com/HtmlUnit/htmlunit/releases/tag/2.70.0
