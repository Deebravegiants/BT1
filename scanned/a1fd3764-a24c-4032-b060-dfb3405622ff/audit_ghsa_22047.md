# [H] Stored XSS vulnerability in Validating String Parameter Plugin

## Summary
Severity: High
Advisory: GHSA-fvwh-wv43-8qj5
CVE: CVE-2020-2257
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fvwh-wv43-8qj5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:validating-string-parameter` — affected >=0 <2.5

## Details
Validating String Parameter Plugin 2.4 and earlier does not escape regular expressions in tooltips. Additionally, Validating String Parameter Plugin 2.4 does not escape parameter names and parameter descriptions.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Job/Configure permission.

Validating String Parameter Plugin 2.5 escapes regular expressions in tooltips and parameter names. Parameter descriptions are rendered using the configured markup formatter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2257
- https://github.com/jenkinsci/validating-string-parameter-plugin/commit/345a79d830a5fcd824a3c755506a438c78c48117
- https://github.com/jenkinsci/validating-string-parameter-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1935
- http://www.openwall.com/lists/oss-security/2020/09/16/3
