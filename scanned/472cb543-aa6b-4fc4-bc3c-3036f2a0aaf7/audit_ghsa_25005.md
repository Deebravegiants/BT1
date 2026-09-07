# [M] XSS vulnerability in Jenkins Markdown Formatter Plugin

## Summary
Severity: Medium
Advisory: GHSA-xqpp-26pp-2365
CVE: CVE-2021-21660
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xqpp-26pp-2365
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:markdown-formatter` — affected >=0 <0.2.0

## Details
Jenkins Markdown Formatter Plugin 0.1.0 and earlier uses a Markdown library to parse Markdown that does not escape crafted link target URLs.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with the ability to edit any description rendered using the configured markup formatter.

Jenkins Markdown Formatter Plugin 0.2.0 uses a different Markdown library that is not affected by this problem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21660
- https://github.com/jenkinsci/markdown-formatter-plugin/commit/6b283a5bba3424fd5174b92e7ad8724cdbdf596c
- https://github.com/jenkinsci/markdown-formatter-plugin
- https://www.jenkins.io/security/advisory/2021-05-25/#SECURITY-2198
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-21660
- http://www.openwall.com/lists/oss-security/2021/05/25/3
