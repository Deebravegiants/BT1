# [M] Jenkins Extensible Choice Parameter Plugin vulnerable to cross-site request forgery

## Summary
Severity: Medium
Advisory: GHSA-3jw2-5hjg-hc2c
CVE: CVE-2025-64133
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-3jw2-5hjg-hc2c
Type: github-advisory

## Affected
- Maven: `jp.ikedam.jenkins.plugins:extensible-choice-parameter` — affected >=0

## Details
Jenkins Extensible Choice Parameter Plugin 239.v5f5c278708cf and earlier does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to execute sandboxed Groovy code.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64133
- https://github.com/jenkinsci/extensible-choice-parameter-plugin
- https://www.jenkins.io/security/advisory/2025-10-29/#SECURITY-3583
- http://www.openwall.com/lists/oss-security/2025/10/29/2
