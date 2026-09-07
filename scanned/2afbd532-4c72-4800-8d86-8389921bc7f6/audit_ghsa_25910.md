# [H] CSRF vulnerability and missing permission check in Jenkins JiraTestResultReporter Plugin

## Summary
Severity: High
Advisory: GHSA-vqcx-jw4r-6fp3
CVE: CVE-2022-28136
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-vqcx-jw4r-6fp3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:JiraTestResultReporter` — affected >=0 <166.v0cc6208295b5

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins JiraTestResultReporter Plugin version 165.v817928553942 and earlier allows attackers to connect to an attacker-specified URL using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28136
- https://github.com/jenkinsci/JiraTestResultReporter-plugin/commit/0cc6208295b5cb683528e8bf04d139f0bee8eb53
- https://github.com/jenkinsci/JiraTestResultReporter-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2236
- http://www.openwall.com/lists/oss-security/2022/03/29/1
