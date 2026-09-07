# [M] Stored Cross-Site Scripting Vulnerability in Jenkins Shelve Project Plugin

## Summary
Severity: Medium
Advisory: GHSA-7577-f8fp-5977
CVE: CVE-2018-1999029
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-7577-f8fp-5977
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:shelve-project-plugin` — affected >=0 <2.0

## Details
A cross-site scripting vulnerability exists in Jenkins Shelve Project Plugin 1.5 and earlier in ShelveProjectAction/index.jelly, ShelvedProjectsAction/index.jelly that allows attackers with Job/Configure permission to define JavaScript that would be executed in another user's browser when that other user performs some UI actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999029
- https://jenkins.io/security/advisory/2018-07-30/#SECURITY-1001
