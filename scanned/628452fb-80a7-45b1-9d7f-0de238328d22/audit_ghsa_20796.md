# [H] Jenkins Anchore Container Image Scanner Plugin vulnerable to cross site scripting

## Summary
Severity: High
Advisory: GHSA-f2j5-w76m-3rqh
CVE: CVE-2022-41225
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-f2j5-w76m-3rqh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:anchore-container-scanner` — affected >=0 <1.0.25

## Details
Jenkins Anchore Container Image Scanner Plugin 1.0.24 and earlier does not escape content provided by the Anchore engine API, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control API responses by Anchore engine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41225
- https://github.com/jenkinsci/anchore-container-scanner-plugin/commit/1b1a62ab8ab86b409274e755860ab4e7fcc11800
- https://github.com/jenkinsci/anchore-container-scanner-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2821
