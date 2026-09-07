# [H] Reflected XSS vulnerability in Jenkins JSGames Plugin

## Summary
Severity: High
Advisory: GHSA-7hf3-h28p-q6gx
CVE: CVE-2020-2248
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7hf3-h28p-q6gx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jsgames` — affected >=0

## Details
Jenkins JSGames Plugin 0.2 and earlier evaluates part of a URL as code, resulting in a reflected cross-site scripting (XSS) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2248
- https://github.com/jenkinsci/jsgames-plugin
- https://jenkins.io/security/advisory/2020-09-01/#SECURITY-1905
- http://www.openwall.com/lists/oss-security/2020/09/01/3
